"""Financial Digital Twin simulation engine.

Scenarios never touch the organization's real transactions/invoices — they
operate on in-memory copies produced here, and are compared against a
baseline forecast computed from the same unmodified inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.forecasting.engine import ForecastPointData, run_forecast
from app.models.financial import Invoice, RecurringObligation, Transaction

TWO_PLACES = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES)


@dataclass
class ScenarioAssumptions:
    customer_payment_delay_days: int = 0
    supplier_payment_delay_days: int = 0
    revenue_change_pct: Decimal = Decimal("0")
    expense_change_pct: Decimal = Decimal("0")
    inventory_purchase_amount: Decimal = Decimal("0")
    financing_amount: Decimal = Decimal("0")
    financing_monthly_cost: Decimal = Decimal("0")
    one_time_cash_injection: Decimal = Decimal("0")


@dataclass
class SimulationOutput:
    baseline_points: list[ForecastPointData]
    simulated_points: list[ForecastPointData]
    lowest_cash_point: Decimal
    lowest_cash_date: date | None
    runway_days: int | None
    days_below_zero: int
    impact_vs_baseline: Decimal
    assumptions: ScenarioAssumptions


def _copy_invoice(inv: Invoice, extra_delay_days: int, as_of: date) -> SimpleNamespace:
    due = inv.due_date
    if inv.status != "paid" and due >= as_of and extra_delay_days:
        due = due + timedelta(days=extra_delay_days)
        # Clamp inside the forecast window: a due date pushed before "tomorrow"
        # (e.g. accelerating collection of an invoice due in 5 days by 10 days)
        # must still land on the earliest day the forecast can represent it,
        # not disappear before the horizon starts.
        earliest = as_of + timedelta(days=1)
        if due < earliest:
            due = earliest
    return SimpleNamespace(
        direction=inv.direction,
        amount=inv.amount,
        amount_paid=inv.amount_paid,
        due_date=due,
        status=inv.status,
    )


def _apply_assumptions(
    transactions: list[Transaction],
    invoices: list[Invoice],
    recurring: list[RecurringObligation],
    as_of: date,
    assumptions: ScenarioAssumptions,
) -> tuple[list, list, list]:
    adjusted_invoices = [
        _copy_invoice(
            inv,
            assumptions.customer_payment_delay_days if inv.direction == "RECEIVABLE" else 0,
            as_of,
        )
        if inv.direction == "RECEIVABLE"
        else _copy_invoice(inv, assumptions.supplier_payment_delay_days, as_of)
        for inv in invoices
    ]

    # One-time events are modeled as synthetic "invoices" due the day after as_of
    # so they flow through the same known-component logic as everything else.
    synthetic_day = as_of + timedelta(days=1)
    if assumptions.inventory_purchase_amount:
        adjusted_invoices.append(
            SimpleNamespace(
                direction="PAYABLE",
                amount=assumptions.inventory_purchase_amount,
                amount_paid=Decimal("0"),
                due_date=synthetic_day,
                status="unpaid",
            )
        )
    if assumptions.financing_amount:
        adjusted_invoices.append(
            SimpleNamespace(
                direction="RECEIVABLE",
                amount=assumptions.financing_amount,
                amount_paid=Decimal("0"),
                due_date=synthetic_day,
                status="unpaid",
            )
        )
    if assumptions.one_time_cash_injection:
        adjusted_invoices.append(
            SimpleNamespace(
                direction="RECEIVABLE",
                amount=assumptions.one_time_cash_injection,
                amount_paid=Decimal("0"),
                due_date=synthetic_day,
                status="unpaid",
            )
        )

    adjusted_recurring = list(recurring)
    if assumptions.financing_monthly_cost:
        adjusted_recurring.append(
            SimpleNamespace(
                name="Financing repayment",
                amount=assumptions.financing_monthly_cost,
                category="financing",
                frequency="monthly",
                next_due_date=synthetic_day,
                direction="OUT",
            )
        )

    return transactions, adjusted_invoices, adjusted_recurring


def run_simulation(
    starting_cash: Decimal,
    transactions: list[Transaction],
    invoices: list[Invoice],
    recurring: list[RecurringObligation],
    as_of: date,
    horizon_days: int,
    assumptions: ScenarioAssumptions,
) -> SimulationOutput:
    baseline_points = run_forecast(starting_cash, transactions, invoices, recurring, as_of, horizon_days)

    adj_tx, adj_invoices, adj_recurring = _apply_assumptions(
        transactions, invoices, recurring, as_of, assumptions
    )

    simulated_points = run_forecast(starting_cash, adj_tx, adj_invoices, adj_recurring, as_of, horizon_days)

    # Apply revenue/expense percentage shocks directly to the uncertain component,
    # which represents day-to-day business-as-usual flow not already tied to a
    # specific invoice or obligation.
    rev_mult = Decimal("1") + (assumptions.revenue_change_pct / Decimal("100"))
    exp_mult = Decimal("1") + (assumptions.expense_change_pct / Decimal("100"))
    running = Decimal(starting_cash)
    adjusted_points: list[ForecastPointData] = []
    for p in simulated_points:
        uncertain = p.uncertain_component
        if uncertain > 0:
            uncertain = _q(uncertain * rev_mult)
        elif uncertain < 0:
            uncertain = _q(uncertain * exp_mult)
        running = _q(running + p.known_component + uncertain)
        adjusted_points.append(
            ForecastPointData(
                date=p.date,
                projected_cash=running,
                known_component=p.known_component,
                uncertain_component=uncertain,
                confidence=p.confidence,
            )
        )

    lowest = min(adjusted_points, key=lambda p: p.projected_cash) if adjusted_points else None
    days_below_zero = sum(1 for p in adjusted_points if p.projected_cash < 0)

    runway_days: int | None = None
    for idx, p in enumerate(adjusted_points):
        if p.projected_cash < 0:
            runway_days = idx + 1
            break

    baseline_final = baseline_points[-1].projected_cash if baseline_points else starting_cash
    simulated_final = adjusted_points[-1].projected_cash if adjusted_points else starting_cash
    impact = _q(simulated_final - baseline_final)

    return SimulationOutput(
        baseline_points=baseline_points,
        simulated_points=adjusted_points,
        lowest_cash_point=lowest.projected_cash if lowest else starting_cash,
        lowest_cash_date=lowest.date if lowest else None,
        runway_days=runway_days,
        days_below_zero=days_below_zero,
        impact_vs_baseline=impact,
        assumptions=assumptions,
    )
