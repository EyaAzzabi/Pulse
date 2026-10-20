"""Deterministic tools the copilot's language model can call. Every number an
answer contains comes from one of these functions; the model only decides which
to call, with which arguments, and how to phrase the results.

Each tool belongs to one of the specialist agents so the UI can show who did
what. The Risk Guardian is not a tool: it is the permission and scope check
applied before a tool runs."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.api.deps import ROLE_RANK
from app.financial.engine import compute_summary
from app.forecasting.engine import find_shortfall, run_forecast
from app.models.financial import Invoice
from app.models.simulation import ActionProposal
from app.services.rescue_plans import generate_rescue_plans
from app.services.workflows import build_invoice_reminder_draft
from app.simulations.engine import ScenarioAssumptions, run_simulation

MAX_HORIZON = 180


@dataclass
class AgentContext:
    db: Session
    organization_id: str
    organization_name: str
    user_id: str
    role: str
    currency: str
    starting_cash: Decimal
    transactions: list
    invoices: list
    recurring: list
    as_of: date
    chart_points: list[dict] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)


class ToolDenied(Exception):
    pass


def _money(v: Decimal) -> str:
    return str(Decimal(v).quantize(Decimal("0.01")))


def _horizon(args: dict) -> int:
    return max(7, min(int(args.get("horizon_days") or 90), MAX_HORIZON))


def get_financial_summary(ctx: AgentContext, args: dict) -> dict:
    s = compute_summary(ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of)
    return {
        "as_of": ctx.as_of.isoformat(),
        "currency": ctx.currency,
        "current_cash": _money(s.current_cash),
        "net_cash_flow_30d": _money(s.net_cash_flow_30d),
        "inflow_30d": _money(s.trailing_30d_inflow),
        "outflow_30d": _money(s.trailing_30d_outflow),
        "monthly_burn_rate": _money(s.monthly_burn_rate),
        "cash_runway_days": s.cash_runway_days,
        "outstanding_receivables": _money(s.outstanding_receivables),
        "outstanding_payables": _money(s.outstanding_payables),
        "overdue_receivables_count": s.overdue_receivables_count,
        "overdue_receivables_amount": _money(s.overdue_receivables_amount),
        "upcoming_obligations_30d": _money(s.upcoming_obligations_30d),
        "largest_customer_share_pct": _money(s.largest_customer_share_pct),
        "risk_level": s.risk_level,
        "risk_reasons": s.risk_reasons,
    }


def _points(points) -> list[dict]:
    return [{"date": p.date.isoformat(), "projected_cash": _money(p.projected_cash), "confidence": p.confidence} for p in points]


def forecast_cash(ctx: AgentContext, args: dict) -> dict:
    horizon = _horizon(args)
    points = run_forecast(ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of, horizon)
    ctx.chart_points = _points(points)
    shortfall = find_shortfall(points)
    lowest = min(points, key=lambda p: p.projected_cash)
    return {
        "horizon_days": horizon,
        "ending_cash": _money(points[-1].projected_cash),
        "lowest_cash": _money(lowest.projected_cash),
        "lowest_cash_date": lowest.date.isoformat(),
        "first_shortfall_date": shortfall.date.isoformat() if shortfall else None,
        "days_below_zero": sum(1 for p in points if p.projected_cash < 0),
        "confidence_note": "First 14 days high confidence, up to 45 days medium, beyond that low.",
    }


SCENARIO_FIELDS = (
    "customer_payment_delay_days",
    "supplier_payment_delay_days",
    "revenue_change_pct",
    "expense_change_pct",
    "inventory_purchase_amount",
    "financing_amount",
    "financing_monthly_cost",
    "one_time_cash_injection",
)


def simulate_scenario(ctx: AgentContext, args: dict) -> dict:
    horizon = _horizon(args)
    values = {}
    for f in SCENARIO_FIELDS:
        raw = args.get(f)
        if raw in (None, ""):
            continue
        values[f] = int(raw) if f.endswith("_days") else Decimal(str(raw))
    customer = (args.get("customer_name") or "").strip() or None
    if customer and not any(
        customer.lower() in (i.counterparty_name or "").lower() for i in ctx.invoices if i.direction == "RECEIVABLE"
    ):
        return {"error": f"No customer invoices found for '{customer}'. Call list_invoices to see customer names."}
    assumptions = ScenarioAssumptions(**values, delayed_customer=customer)
    out = run_simulation(ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of, horizon, assumptions)
    ctx.chart_points = _points(out.simulated_points)
    base_low = min(p.projected_cash for p in out.baseline_points)
    return {
        "assumptions": {k: str(v) for k, v in values.items()} | ({"delayed_customer": customer} if customer else {}),
        "horizon_days": horizon,
        "baseline_lowest_cash": _money(base_low),
        "simulated_lowest_cash": _money(out.lowest_cash_point),
        "simulated_lowest_cash_date": out.lowest_cash_date.isoformat() if out.lowest_cash_date else None,
        "simulated_days_below_zero": out.days_below_zero,
        "change_in_lowest_cash": _money(out.lowest_cash_point - base_low),
        "ending_cash_vs_baseline": _money(out.impact_vs_baseline),
        "days_until_first_shortfall": out.runway_days,
    }


def get_rescue_plans(ctx: AgentContext, args: dict) -> dict:
    plans = generate_rescue_plans(ctx.starting_cash, ctx.transactions, ctx.invoices, ctx.recurring, ctx.as_of)
    return {
        "plans": [
            {
                "title": p.title,
                "rationale": p.rationale,
                "estimated_liquidity_benefit": _money(p.estimated_liquidity_benefit),
                "feasibility": p.feasibility,
                "cost": p.cost,
                "residual_risk": p.residual_risk,
            }
            for p in plans
        ],
        "note": "Ranked by simulated improvement of the lowest projected cash point. None are guaranteed.",
    }


def list_invoices(ctx: AgentContext, args: dict) -> dict:
    direction = (args.get("direction") or "").upper() or None
    status = (args.get("status") or "").lower() or None
    rows = []
    for inv in sorted(ctx.invoices, key=lambda i: i.due_date):
        if direction and inv.direction != direction:
            continue
        overdue = inv.status != "paid" and inv.due_date < ctx.as_of
        effective = "overdue" if overdue else inv.status
        if status and effective != status:
            continue
        rows.append(
            {
                "id": inv.id,
                "counterparty": inv.counterparty_name,
                "direction": inv.direction,
                "outstanding": _money(inv.amount - inv.amount_paid),
                "due_date": inv.due_date.isoformat(),
                "days_overdue": (ctx.as_of - inv.due_date).days if overdue else 0,
                "status": effective,
            }
        )
    return {"count": len(rows), "invoices": rows[:25]}


def propose_invoice_reminder(ctx: AgentContext, args: dict) -> dict:
    # Risk Guardian: drafting is allowed from ACCOUNTANT up; it is never sent here.
    if ROLE_RANK.get(ctx.role, -1) < ROLE_RANK["ACCOUNTANT"]:
        raise ToolDenied("Your role can't draft reminders. Ask an accountant or owner.")
    ids = [str(i) for i in (args.get("invoice_ids") or [])][:10]
    invoices = [
        inv
        for inv in ctx.db.query(Invoice).filter(Invoice.organization_id == ctx.organization_id, Invoice.id.in_(ids)).all()
        if inv.direction == "RECEIVABLE" and inv.status != "paid"
    ]
    if not invoices:
        return {"created": False, "reason": "No matching unpaid customer invoices. Call list_invoices first to get ids."}
    drafts = [build_invoice_reminder_draft(inv, ctx.organization_name, inv.currency) for inv in invoices]
    action = ActionProposal(
        organization_id=ctx.organization_id,
        created_by_user_id=ctx.user_id,
        action_type="send_invoice_reminder",
        target_json=json.dumps({"invoice_ids": [i.id for i in invoices]}),
        details_json=json.dumps({"drafts": drafts, "proposed_by": "copilot"}),
        expected_result=f"{len(drafts)} reminder email(s) prepared for review.",
        risks="Low. No funds move. Customers receive a payment reminder only after approval.",
        evidence_json=json.dumps(
            {"invoices": [{"id": i.id, "counterparty_name": i.counterparty_name, "outstanding": _money(i.amount - i.amount_paid)} for i in invoices]}
        ),
        requires_approval=True,
        status="PENDING_APPROVAL",
        execution_result_json="{}",
    )
    ctx.db.add(action)
    ctx.db.commit()
    ctx.actions.append({"id": action.id, "action_type": action.action_type, "status": action.status, "count": len(drafts)})
    return {
        "created": True,
        "action_id": action.id,
        "status": "PENDING_APPROVAL",
        "invoices": [i.counterparty_name for i in invoices],
        "next_step": "Tell the user it is waiting for approval in the Decision Center. Nothing has been sent.",
    }


TOOLS = {
    "get_financial_summary": {
        "agent": "Financial Analyst",
        "fn": get_financial_summary,
        "description": "Current cash, 30-day flows, burn rate, runway, receivables, payables, risk level and reasons.",
        "parameters": {"type": "object", "properties": {}},
    },
    "forecast_cash": {
        "agent": "Forecast Analyst",
        "fn": forecast_cash,
        "description": "Deterministic cash forecast: lowest point, first shortfall date, days below zero.",
        "parameters": {
            "type": "object",
            "properties": {"horizon_days": {"type": "integer", "description": "7 to 180, default 90"}},
        },
    },
    "simulate_scenario": {
        "agent": "Strategic Planner",
        "fn": simulate_scenario,
        "description": (
            "What-if simulation against the baseline forecast. Use for any hypothetical: late payments, purchases, "
            "financing, revenue or expense changes. Real records are never modified."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_payment_delay_days": {"type": "integer", "description": "Extra days customers pay late (negative = earlier)"},
                "customer_name": {
                    "type": "string",
                    "description": "Apply the payment delay to this one customer only. Omit to delay all customers.",
                },
                "supplier_payment_delay_days": {"type": "integer", "description": "Extra days before paying suppliers"},
                "revenue_change_pct": {"type": "number"},
                "expense_change_pct": {"type": "number"},
                "inventory_purchase_amount": {"type": "number", "description": "One-off purchase paid tomorrow"},
                "financing_amount": {"type": "number", "description": "Loan received tomorrow"},
                "financing_monthly_cost": {"type": "number", "description": "Monthly repayment for that loan"},
                "one_time_cash_injection": {"type": "number"},
                "horizon_days": {"type": "integer"},
            },
        },
    },
    "get_rescue_plans": {
        "agent": "Strategic Planner",
        "fn": get_rescue_plans,
        "description": "Ranked candidate strategies to avoid a shortfall, each with its simulated benefit.",
        "parameters": {"type": "object", "properties": {}},
    },
    "list_invoices": {
        "agent": "Financial Analyst",
        "fn": list_invoices,
        "description": "Invoices with ids, counterparty, outstanding amount, due date and days overdue.",
        "parameters": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["RECEIVABLE", "PAYABLE"]},
                "status": {"type": "string", "enum": ["overdue", "unpaid", "paid"]},
            },
        },
    },
    "propose_invoice_reminder": {
        "agent": "Workflow Coordinator",
        "fn": propose_invoice_reminder,
        "description": (
            "Drafts reminder emails for unpaid customer invoices and files them in the Decision Center for human "
            "approval. Never sends anything. Use only when the user asks to prepare or send reminders."
        ),
        "parameters": {
            "type": "object",
            "properties": {"invoice_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["invoice_ids"],
        },
    },
}


def openai_tool_specs() -> list[dict]:
    return [
        {"type": "function", "function": {"name": name, "description": t["description"], "parameters": t["parameters"]}}
        for name, t in TOOLS.items()
    ]


def run_tool(ctx: AgentContext, name: str, args: dict) -> tuple[str, dict]:
    """Returns (agent name, result). Unknown tools and denials come back as
    results rather than exceptions so the model can explain them."""
    tool = TOOLS.get(name)
    if not tool:
        return "Risk Guardian", {"error": f"Unknown tool '{name}'."}
    try:
        return tool["agent"], tool["fn"](ctx, args or {})
    except ToolDenied as exc:
        return "Risk Guardian", {"error": str(exc), "blocked": True}
    except (ValueError, TypeError) as exc:
        return tool["agent"], {"error": f"Invalid arguments: {exc}"}
