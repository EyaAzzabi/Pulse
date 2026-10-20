"""Deterministic cash-flow forecasting baseline.

Each projected day separates a KNOWN component (recurring obligations and
invoice due dates already on record) from an UNCERTAIN component (a flat
daily estimate derived from trailing historical net cash flow, standing in
for day-to-day revenue/expenses that are not tied to a specific scheduled
record). This keeps the forecast auditable: every number traces back either
to a stored obligation/invoice or to an explicit historical average.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.financial.engine import current_liquidity, net_cash_flow
from app.models.financial import Invoice, RecurringObligation, Transaction

TWO_PLACES = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES)


@dataclass
class ForecastPointData:
    date: date
    projected_cash: Decimal
    known_component: Decimal
    uncertain_component: Decimal
    confidence: str


def _daily_baseline_flow(
    transactions: list[Transaction],
    as_of: date,
    exclude_categories: set[str],
    lookback_days: int = 90,
) -> Decimal:
    """Average daily net flow from history, EXCLUDING categories that are
    already represented going forward as explicit recurring obligations
    (e.g. rent, payroll, software). Without this exclusion those costs would
    be subtracted twice: once implicitly (they lower the historical net
    average) and once explicitly via the known recurring-obligation
    component, which would overstate future cash burn."""
    if lookback_days <= 0:
        return Decimal("0.00")
    filtered = [t for t in transactions if t.category not in exclude_categories]
    _, _, net = net_cash_flow(filtered, as_of - timedelta(days=lookback_days), as_of)
    return _q(net / Decimal(lookback_days))


def _known_component_for_day(
    day: date, recurring: list[RecurringObligation], invoices: list[Invoice]
) -> Decimal:
    total = Decimal("0")
    for ob in recurring:
        due = ob.next_due_date
        if ob.frequency == "monthly":
            # Project monthly recurrence forward by matching day-of-month.
            if due.day == day.day and day >= due:
                total += ob.amount if ob.direction == "IN" else -ob.amount
        elif ob.frequency == "weekly":
            if due <= day and (day - due).days % 7 == 0:
                total += ob.amount if ob.direction == "IN" else -ob.amount
    for inv in invoices:
        if inv.status == "paid":
            continue
        remaining = inv.amount - inv.amount_paid
        if inv.due_date == day:
            total += remaining if inv.direction == "RECEIVABLE" else -remaining
    return total


def _confidence_for_horizon(day_offset: int, has_sufficient_history: bool) -> str:
    if not has_sufficient_history:
        return "low"
    if day_offset <= 14:
        return "high"
    if day_offset <= 45:
        return "medium"
    return "low"


def run_forecast(
    starting_cash: Decimal,
    transactions: list[Transaction],
    invoices: list[Invoice],
    recurring: list[RecurringObligation],
    as_of: date,
    horizon_days: int = 90,
) -> list[ForecastPointData]:
    has_sufficient_history = len(transactions) >= 30
    recurring_categories = {ob.category for ob in recurring}
    baseline_daily_flow = _daily_baseline_flow(transactions, as_of, recurring_categories)

    points: list[ForecastPointData] = []
    # `starting_cash` is the opening balance before the first recorded
    # transaction; the forecast has to start from today's position.
    running_cash = current_liquidity(starting_cash, transactions, as_of)
    for offset in range(1, horizon_days + 1):
        day = as_of + timedelta(days=offset)
        known = _q(_known_component_for_day(day, recurring, invoices))
        uncertain = baseline_daily_flow if has_sufficient_history else Decimal("0.00")
        running_cash = _q(running_cash + known + uncertain)
        points.append(
            ForecastPointData(
                date=day,
                projected_cash=running_cash,
                known_component=known,
                uncertain_component=uncertain,
                confidence=_confidence_for_horizon(offset, has_sufficient_history),
            )
        )
    return points


def find_shortfall(points: list[ForecastPointData]) -> ForecastPointData | None:
    for point in points:
        if point.projected_cash < 0:
            return point
    return None
