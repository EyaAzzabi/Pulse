"""Agent 6 — Orchestrator.

Classifies the user's intent, invokes the relevant deterministic financial
tools (Agent 1 Financial Analyst / Agent 2 Forecast Analyst / Agent 3
Strategic Planner), and builds a grounded response. If an LLM is configured,
it is asked only to phrase the already-computed numbers in natural language
(Agent 4 Risk Guardian's rule: the LLM may explain, never invent, a figure).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from app.agents import llm_provider
from app.financial.engine import compute_summary
from app.forecasting.engine import find_shortfall, run_forecast
from app.services.rescue_plans import generate_rescue_plans

HORIZON_DAYS = 90


@dataclass
class CopilotResponse:
    message: str
    ai_generated: bool
    metrics: dict = field(default_factory=dict)
    risk_indicators: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    suggested_follow_ups: list[str] = field(default_factory=list)
    chart_points: list[dict] = field(default_factory=list)


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
