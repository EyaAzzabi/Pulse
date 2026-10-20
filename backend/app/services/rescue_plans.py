"""Strategic Planner support: generates candidate rescue strategies by running
the same deterministic simulation engine used by the Digital Twin, so every
"expected impact" number is a real simulated outcome rather than a guess."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.simulations.engine import ScenarioAssumptions, run_simulation

CANDIDATES = [
    {
        "key": "accelerate_collections",
        "title": "Collect overdue invoices",
        "rationale": (
            "Send reminders on every overdue customer invoice and assume they are paid within 7 days. "
            "Future invoices are also chased 10 days earlier."
        ),
        "assumptions": ScenarioAssumptions(customer_payment_delay_days=-10, collect_overdue_within_days=7),
        "feasibility": "medium",
        "cost": "low",
    },
    {
        "key": "extend_supplier_terms",
        "title": "Negotiate supplier payment extensions",
        "rationale": "Ask suppliers for 15 more days on upcoming bills to keep cash in the business longer.",
        "assumptions": ScenarioAssumptions(supplier_payment_delay_days=15),
        "feasibility": "medium",
        "cost": "low",
    },
    {
        "key": "short_term_credit",
        "title": "Bridge with a short-term credit line",
        "rationale": (
            "Draw 5,000 from a credit line repaid at about 440 per month. Illustrative terms only, "
            "not a lender offer."
        ),
        "assumptions": ScenarioAssumptions(
            financing_amount=Decimal("5000"), financing_monthly_cost=Decimal("440")
        ),
        "feasibility": "medium",
        "cost": "high",
    },
]


@dataclass
class RescuePlanCandidate:
    key: str
    title: str
    rationale: str
    feasibility: str
    cost: str
    estimated_liquidity_benefit: Decimal
    residual_risk: str
    assumptions: ScenarioAssumptions


def generate_rescue_plans(
    starting_cash: Decimal, transactions, invoices, recurring, as_of: date, horizon_days: int = 90
) -> list[RescuePlanCandidate]:
    baseline = run_simulation(
        starting_cash, transactions, invoices, recurring, as_of, horizon_days, ScenarioAssumptions()
    )
    results: list[RescuePlanCandidate] = []
    for candidate in CANDIDATES:
        sim = run_simulation(
            starting_cash, transactions, invoices, recurring, as_of, horizon_days, candidate["assumptions"]
        )
        benefit = sim.lowest_cash_point - baseline.lowest_cash_point
        residual_risk = "low" if sim.days_below_zero == 0 else ("medium" if sim.days_below_zero < 15 else "high")
        results.append(
            RescuePlanCandidate(
                key=candidate["key"],
                title=candidate["title"],
                rationale=candidate["rationale"],
                feasibility=candidate["feasibility"],
                cost=candidate["cost"],
                estimated_liquidity_benefit=benefit,
                residual_risk=residual_risk,
                assumptions=candidate["assumptions"],
            )
        )
    results.sort(key=lambda r: r.estimated_liquidity_benefit, reverse=True)
    return results
