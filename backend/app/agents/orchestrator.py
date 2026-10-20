"""Agent 6 — Orchestrator.

Classifies the user's intent, invokes the relevant deterministic financial
tools (Agent 1 Financial Analyst / Agent 2 Forecast Analyst / Agent 3
Strategic Planner), and builds a grounded response. If an LLM is configured,
it is asked only to phrase the already-computed numbers in natural language
(Agent 4 Risk Guardian's rule: the LLM may explain, never invent, a figure).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from app.agents import llm_provider
from app.agents.tools import AgentContext, openai_tool_specs, run_tool
from app.financial.engine import compute_summary
from app.forecasting.engine import find_shortfall, run_forecast
from app.services.rescue_plans import generate_rescue_plans

logger = logging.getLogger(__name__)

HORIZON_DAYS = 90
MAX_AGENT_STEPS = 6


@dataclass
class CopilotResponse:
    message: str
    ai_generated: bool
    metrics: dict = field(default_factory=dict)
    risk_indicators: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    suggested_follow_ups: list[str] = field(default_factory=list)
    chart_points: list[dict] = field(default_factory=list)
    agent_trace: list[dict] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)


AGENT_SYSTEM_PROMPT = """You are PULSE AI, the financial copilot of {org}, an SME. Today is {today}. Currency: {currency}.
You coordinate specialist agents through tools: Financial Analyst (summary, invoices), Forecast Analyst (forecast),
Strategic Planner (simulations, rescue plans) and Workflow Coordinator (reminder drafts).

Rules:
- Every number you state must come from a tool result in this conversation. Never estimate or invent figures,
  dates, customers or outcomes. If no tool gives it, say you don't have that information.
- For any what-if question (late payments, a purchase, a loan, revenue or cost changes), call simulate_scenario
  with the user's numbers and compare it with the baseline.
- To draft reminders, call list_invoices first for ids, then propose_invoice_reminder. Reminders are only drafts
  waiting for human approval in the Decision Center; never say anything was sent.
- Forecasts and simulations are estimates, not guarantees. Mention uncertainty when it matters.
- PULSE is decision support, not a regulated financial adviser. It never moves money.
- Answer in the user's language, concisely: a direct answer first, then 2 to 4 short supporting points.
  Format amounts like "{currency} 12,500.00"."""


def _short(v) -> str:
    try:
        return f"{Decimal(str(v)):,.0f}"
    except Exception:
        return str(v)


def _trace_summary(tool: str, args: dict, result: dict) -> str:
    if result.get("error"):
        return result["error"]
    if tool == "get_financial_summary":
        return f"Cash {_short(result['current_cash'])}, risk {result['risk_level']}"
    if tool == "forecast_cash":
        short = result.get("first_shortfall_date")
        return f"{result['horizon_days']}-day forecast, lowest {_short(result['lowest_cash'])}" + (f", shortfall {short}" if short else "")
    if tool == "simulate_scenario":
        changes = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in result["assumptions"].items()) or "baseline"
        return f"Simulated {changes}: lowest {_short(result['simulated_lowest_cash'])} vs {_short(result['baseline_lowest_cash'])}"
    if tool == "get_rescue_plans":
        top = result["plans"][0] if result["plans"] else None
        return f"Ranked {len(result['plans'])} strategies" + (f", best: {top['title']}" if top else "")
    if tool == "list_invoices":
        return f"Found {result['count']} invoice(s)"
    if tool == "propose_invoice_reminder":
        return "Reminder draft filed for approval" if result.get("created") else result.get("reason", "No draft created")
    return "Done"


INTENT_TRACE = {
    "cash_runway": ("Financial Analyst", "get_financial_summary"),
    "biggest_risk": ("Financial Analyst", "get_financial_summary"),
    "general_summary": ("Financial Analyst", "get_financial_summary"),
    "affordability": ("Financial Analyst", "get_financial_summary"),
    "simulate": ("Forecast Analyst", "forecast_cash"),
    "rescue_plan": ("Strategic Planner", "get_rescue_plans"),
    "invoice_reminders": ("Financial Analyst", "list_invoices"),
}


def run_agent(message: str, history: list[dict], ctx: AgentContext, tone: str = "concise") -> CopilotResponse:
    """Tool-calling agent loop when an LLM is configured; the deterministic
    keyword path otherwise, or whenever the LLM call fails."""
    summary = compute_summary(ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of)
    base = _base_context(summary, ctx.as_of, ctx.currency)

    if llm_provider.is_llm_configured():
        try:
            return _agent_loop(message, history, ctx, base)
        except Exception:
            logger.exception("Agent loop failed; using deterministic copilot")

    result = handle_message(
        message, ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of, ctx.currency,
        tone=tone, history=history,
    )
    agent, tool = INTENT_TRACE[classify_intent(message)]
    result.agent_trace = [{"agent": agent, "tool": tool, "summary": "Deterministic mode (no LLM tool calling)"}]
    return result


def _agent_loop(message: str, history: list[dict], ctx: AgentContext, base: dict) -> CopilotResponse:
    messages: list[dict] = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT.format(org=ctx.organization_name, today=ctx.as_of.isoformat(), currency=ctx.currency),
        },
        *history[-8:],
        {"role": "user", "content": message},
    ]
    specs = openai_tool_specs()
    trace: list[dict] = []
    text = ""
    for _ in range(MAX_AGENT_STEPS):
        reply = llm_provider.chat_with_tools(messages, specs)
        calls = reply.get("tool_calls") or []
        if not calls:
            text = (reply.get("content") or "").strip()
            break
        messages.append({"role": "assistant", "content": reply.get("content"), "tool_calls": calls})
        for call in calls:
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            agent, result = run_tool(ctx, name, args)
            trace.append({"agent": agent, "tool": name, "summary": _trace_summary(name, args, result)})
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result, default=str)})
    if not text:
        raise RuntimeError("Agent did not produce a final answer")

    trace.append({"agent": "Risk Guardian", "tool": "review", "summary": "Answer limited to tool results; no actions executed"})
    return CopilotResponse(
        message=text,
        ai_generated=True,
        metrics=base["metrics"],
        risk_indicators=base["risk_reasons"],
        evidence=base["evidence"],
        suggested_follow_ups=_follow_ups(trace),
        chart_points=ctx.chart_points,
        agent_trace=trace,
        actions=ctx.actions,
    )


def _follow_ups(trace: list[dict]) -> list[str]:
    used = {t["tool"] for t in trace}
    options = [
        ("simulate_scenario", "What if my largest customer pays 20 days late?"),
        ("get_rescue_plans", "How can I avoid a cash shortage?"),
        ("forecast_cash", "When is my lowest cash point in the next 90 days?"),
        ("propose_invoice_reminder", "Prepare reminders for my overdue invoices."),
    ]
    return [q for tool, q in options if tool not in used][:3]


def _base_context(summary, as_of: date, currency: str) -> dict:
    return {
        "metrics": {
            "current_cash": str(summary.current_cash),
            "cash_runway_days": summary.cash_runway_days,
            "monthly_burn_rate": str(summary.monthly_burn_rate),
            "net_cash_flow_30d": str(summary.net_cash_flow_30d),
            "overdue_receivables_amount": str(summary.overdue_receivables_amount),
            "risk_level": summary.risk_level,
        },
        "risk_reasons": summary.risk_reasons,
        "evidence": [
            f"Current cash balance as of {as_of.isoformat()}: {_money(summary.current_cash, currency)}.",
            f"Net cash flow (last 30 days): {_money(summary.net_cash_flow_30d, currency)}.",
            f"Outstanding receivables: {_money(summary.outstanding_receivables, currency)} "
            f"({summary.overdue_receivables_count} overdue for {_money(summary.overdue_receivables_amount, currency)}).",
        ],
    }


def classify_intent(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["simulate", "what if", "what happens if", "delay", "late"]):
        return "simulate"
    if any(k in text for k in ["afford", "purchase", "buy", "can i spend"]):
        return "affordability"
    if any(k in text for k in ["remind", "overdue", "collect", "follow up", "follow-up"]):
        return "invoice_reminders"
    if any(k in text for k in ["rescue", "strategy", "recommend", "improve", "avoid a", "how can i"]):
        return "rescue_plan"
    if any(k in text for k in ["runway", "how long", "last"]):
        return "cash_runway"
    if any(k in text for k in ["risk", "biggest", "worry", "concern"]):
        return "biggest_risk"
    return "general_summary"


def _money(amount: Decimal, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def _summary_context(starting_cash, transactions, invoices, recurring, as_of, currency):
    summary = compute_summary(starting_cash, transactions, invoices, recurring, as_of)
    return summary


def handle_message(
    message: str,
    starting_cash: Decimal,
    transactions,
    invoices,
    recurring,
    as_of: date,
    currency: str,
    tone: str = "concise",
    history: list[dict] | None = None,
) -> CopilotResponse:
    """`history` is prior turns in this conversation ([{"role": "user"|"assistant", "content": ...}, ...],
    oldest first, NOT including the current `message`). It gives the LLM short-term memory of the
    conversation so far — it is never used to source facts, only to keep the phrasing coherent across
    turns; every figure still comes exclusively from the deterministic summary computed below."""
    intent = classify_intent(message)
    summary = _summary_context(starting_cash, transactions, invoices, recurring, as_of, currency)

    metrics: dict = {
        "current_cash": str(summary.current_cash),
        "cash_runway_days": summary.cash_runway_days,
        "monthly_burn_rate": str(summary.monthly_burn_rate),
        "net_cash_flow_30d": str(summary.net_cash_flow_30d),
        "overdue_receivables_amount": str(summary.overdue_receivables_amount),
        "risk_level": summary.risk_level,
    }
    evidence = [
        f"Current cash balance as of {as_of.isoformat()}: {_money(summary.current_cash, currency)}.",
        f"Net cash flow (last 30 days): {_money(summary.net_cash_flow_30d, currency)}.",
        f"Outstanding receivables: {_money(summary.outstanding_receivables, currency)} "
        f"({summary.overdue_receivables_count} overdue for {_money(summary.overdue_receivables_amount, currency)}).",
    ]
    follow_ups = [
        "What is my biggest financial risk?",
        "Simulate a 15-day customer payment delay.",
        "Prepare reminders for my overdue invoices.",
    ]
    chart_points: list[dict] = []
    deterministic_text: str

    if intent == "cash_runway":
        if summary.cash_runway_days is None:
            deterministic_text = (
                f"Your current cash balance is {_money(summary.current_cash, currency)} and your net cash "
                "flow over the last 30 days is not burning cash, so a fixed runway cannot be computed from "
                "current data."
            )
        else:
            deterministic_text = (
                f"At your current monthly burn rate of {_money(summary.monthly_burn_rate, currency)}, "
                f"your cash balance of {_money(summary.current_cash, currency)} gives you an estimated "
                f"runway of {summary.cash_runway_days} days."
            )

    elif intent == "biggest_risk":
        deterministic_text = "Here is what PULSE detected from your current financial data: " + " ".join(
            summary.risk_reasons
        )

    elif intent == "simulate":
        points = run_forecast(starting_cash, transactions, invoices, recurring, as_of, HORIZON_DAYS)
        shortfall = find_shortfall(points)
        chart_points = [
            {"date": p.date.isoformat(), "projected_cash": str(p.projected_cash), "confidence": p.confidence}
            for p in points
        ]
        if shortfall:
            deterministic_text = (
                f"Based on your current data, the baseline forecast projects a cash shortfall around "
                f"{shortfall.date.isoformat()} (projected balance {_money(shortfall.projected_cash, currency)}). "
                "Open the Simulator to test specific interventions such as delayed payments or financing."
            )
        else:
            deterministic_text = (
                f"The baseline {HORIZON_DAYS}-day forecast does not show a cash shortfall from current data. "
                "Use the Simulator to stress-test specific changes such as payment delays or a large purchase."
            )

    elif intent == "affordability":
        deterministic_text = (
            f"Your current cash balance is {_money(summary.current_cash, currency)}. To check whether a "
            "specific purchase is affordable without risking a shortfall, open the Simulator and enter the "
            "purchase amount under 'Inventory purchase' — PULSE will show the resulting lowest projected cash "
            "point before you commit."
        )

    elif intent == "invoice_reminders":
        if summary.overdue_receivables_count:
            deterministic_text = (
                f"You have {summary.overdue_receivables_count} overdue invoice(s) totalling "
                f"{_money(summary.overdue_receivables_amount, currency)}. Open the Invoices workspace to review "
                "them and prepare reminder drafts — nothing is sent without your explicit approval."
            )
        else:
            deterministic_text = "No overdue invoices were found in your current data."

    elif intent == "rescue_plan":
        plans = generate_rescue_plans(starting_cash, transactions, invoices, recurring, as_of, HORIZON_DAYS)
        lines = [
            f"{i + 1}. {p.title} — estimated liquidity benefit {_money(p.estimated_liquidity_benefit, currency)}, "
            f"feasibility {p.feasibility}, residual risk {p.residual_risk}."
            for i, p in enumerate(plans)
        ]
        deterministic_text = (
            "Based on simulated outcomes, here are candidate strategies ranked by estimated liquidity benefit "
            "(none are guaranteed — review assumptions before acting):\n" + "\n".join(lines)
        )

    else:
        deterministic_text = (
            f"Your business pulse: cash balance {_money(summary.current_cash, currency)}, "
            f"30-day net cash flow {_money(summary.net_cash_flow_30d, currency)}, risk level '{summary.risk_level}'. "
            + " ".join(summary.risk_reasons)
        )

    final_text = deterministic_text
    ai_generated = False

    if llm_provider.is_llm_configured():
        tone_instruction = (
            "Answer concisely in 2-3 sentences." if tone == "concise" else "Answer with clear, helpful detail."
        )
        system_prompt = (
            "You are PULSE AI, a financial copilot for SMEs. You must ONLY use the numbers and facts given to "
            "you in the 'Grounded data' section below — never invent balances, dates, or figures. If you are "
            "unsure, say so. Do not claim any forecast is guaranteed. "
            + tone_instruction
        )
        user_prompt = (
            f"User question: {message}\n\n"
            f"Grounded data (already computed by deterministic financial code):\n{deterministic_text}"
        )
        # Short-term memory: recent prior turns give the model conversational continuity
        # (e.g. resolving "what about that one" to the invoice just discussed). They are
        # history for tone/context only — the grounded data above remains the sole source
        # of truth for any figure.
        recent_history = (history or [])[-6:]
        llm_text = llm_provider.complete(
            [
                {"role": "system", "content": system_prompt},
                *recent_history,
                {"role": "user", "content": user_prompt},
            ]
        )
        if llm_text:
            final_text = llm_text
            ai_generated = True

    return CopilotResponse(
        message=final_text,
        ai_generated=ai_generated,
        metrics=metrics,
        risk_indicators=summary.risk_reasons,
        evidence=evidence,
        suggested_follow_ups=follow_ups,
        chart_points=chart_points,
    )
