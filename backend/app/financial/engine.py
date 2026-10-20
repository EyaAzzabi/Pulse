"""Deterministic financial calculations. No LLM involvement — every number here
is derived from stored records using plain arithmetic on Decimal values so that
results are reproducible and auditable.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from app.models.financial import Invoice, RecurringObligation, Transaction

TWO_PLACES = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES)


@dataclass
class FinancialSummary:
    as_of: date
    current_cash: Decimal
    trailing_30d_inflow: Decimal
    trailing_30d_outflow: Decimal
    net_cash_flow_30d: Decimal
    monthly_burn_rate: Decimal
    cash_runway_days: int | None
    outstanding_receivables: Decimal
    outstanding_payables: Decimal
    overdue_receivables_count: int
    overdue_receivables_amount: Decimal
    overdue_payables_count: int
    overdue_payables_amount: Decimal
    upcoming_obligations_30d: Decimal
    largest_customer_share_pct: Decimal
    expense_trend_pct: Decimal
    risk_level: str
    risk_reasons: list[str] = field(default_factory=list)


def current_liquidity(starting_cash: Decimal, transactions: list[Transaction], as_of: date) -> Decimal:
    """Cash balance = provided starting balance plus all posted transactions up to as_of.

    `starting_cash` is expected to represent the cash position BEFORE the earliest
    transaction in `transactions` (i.e. the seed's opening balance), so that summing
    every transaction reproduces the current balance deterministically.
    """
    total = Decimal(starting_cash)
    for t in transactions:
        if t.date <= as_of:
            total += t.amount if t.direction == "IN" else -t.amount
    return _q(total)


def net_cash_flow(transactions: list[Transaction], start: date, end: date) -> tuple[Decimal, Decimal, Decimal]:
    inflow = Decimal("0")
    outflow = Decimal("0")
    for t in transactions:
        if start <= t.date <= end:
            if t.direction == "IN":
                inflow += t.amount
            else:
                outflow += t.amount
    return _q(inflow), _q(outflow), _q(inflow - outflow)


def monthly_burn_rate(transactions: list[Transaction], as_of: date, lookback_days: int = 90) -> Decimal:
    start = as_of - timedelta(days=lookback_days)
    inflow, outflow, _ = net_cash_flow(transactions, start, as_of)
    net = outflow - inflow
    months = Decimal(lookback_days) / Decimal(30)
    if net <= 0 or months == 0:
        return Decimal("0.00")
    return _q(net / months)


def cash_runway_days(current_cash: Decimal, monthly_burn: Decimal) -> int | None:
    if monthly_burn <= 0:
        return None
    daily_burn = monthly_burn / Decimal(30)
    if daily_burn <= 0:
        return None
    return int((current_cash / daily_burn).to_integral_value(rounding="ROUND_FLOOR"))


def outstanding_receivables(invoices: list[Invoice], as_of: date) -> Decimal:
    total = Decimal("0")
    for inv in invoices:
        if inv.direction == "RECEIVABLE" and inv.status != "paid":
            total += inv.amount - inv.amount_paid
    return _q(total)


def outstanding_payables(invoices: list[Invoice], as_of: date) -> Decimal:
    total = Decimal("0")
    for inv in invoices:
        if inv.direction == "PAYABLE" and inv.status != "paid":
            total += inv.amount - inv.amount_paid
    return _q(total)


def overdue_invoices(invoices: list[Invoice], as_of: date, direction: str) -> tuple[int, Decimal]:
    count = 0
    total = Decimal("0")
    for inv in invoices:
        if inv.direction == direction and inv.status != "paid" and inv.due_date < as_of:
            count += 1
            total += inv.amount - inv.amount_paid
    return count, _q(total)


def upcoming_obligations(
    recurring: list[RecurringObligation], invoices: list[Invoice], as_of: date, horizon_days: int = 30
) -> Decimal:
    end = as_of + timedelta(days=horizon_days)
    total = Decimal("0")
    for ob in recurring:
        if ob.direction == "OUT" and as_of <= ob.next_due_date <= end:
            total += ob.amount
    for inv in invoices:
        if inv.direction == "PAYABLE" and inv.status != "paid" and as_of <= inv.due_date <= end:
            total += inv.amount - inv.amount_paid
    return _q(total)


def concentration_risk(invoices: list[Invoice]) -> Decimal:
    """Share of outstanding receivables tied to the single largest customer (%)."""
    by_customer: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    total = Decimal("0")
    for inv in invoices:
        if inv.direction == "RECEIVABLE" and inv.status != "paid":
            outstanding = inv.amount - inv.amount_paid
            by_customer[inv.counterparty_name] += outstanding
            total += outstanding
    if total <= 0 or not by_customer:
        return Decimal("0.00")
    largest = max(by_customer.values())
    return _q((largest / total) * 100)


def expense_trend_pct(transactions: list[Transaction], as_of: date) -> Decimal:
    """Percentage change in outflows: last 30 days vs the prior 30 days."""
    _, recent_out, _ = net_cash_flow(transactions, as_of - timedelta(days=30), as_of)
    _, prior_out, _ = net_cash_flow(transactions, as_of - timedelta(days=60), as_of - timedelta(days=30))
    if prior_out == 0:
        return Decimal("0.00")
    return _q(((recent_out - prior_out) / prior_out) * 100)


def classify_risk(
    current_cash: Decimal,
    runway_days: int | None,
    overdue_receivables_amount: Decimal,
    concentration_pct: Decimal,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    level = "low"

    if runway_days is not None and runway_days < 30:
        level = "high"
        reasons.append(f"Cash runway is only {runway_days} days at the current burn rate.")
    elif runway_days is not None and runway_days < 60:
        level = "medium"
        reasons.append(f"Cash runway is {runway_days} days — worth monitoring.")

    if current_cash < 0:
        level = "high"
        reasons.append("Current cash balance is negative.")

    if overdue_receivables_amount > 0:
        if level == "low":
            level = "medium"
        reasons.append(f"{overdue_receivables_amount} in overdue receivables not yet collected.")

    if concentration_pct >= 50:
        if level == "low":
            level = "medium"
        reasons.append(f"{concentration_pct}% of receivables depend on a single customer.")

    if not reasons:
        reasons.append("No material liquidity risk detected from current data.")

    return level, reasons


def historical_cash_series(
    starting_cash: Decimal, transactions: list[Transaction], start: date, end: date
) -> list[tuple[date, Decimal]]:
    """Daily running cash balance between start and end (inclusive), reconstructed
    by replaying every transaction up to each day on top of the opening balance."""
    running = current_liquidity(starting_cash, transactions, start - timedelta(days=1))
    by_day: dict[date, Decimal] = defaultdict(lambda: Decimal("0"))
    for t in transactions:
        if start <= t.date <= end:
            by_day[t.date] += t.amount if t.direction == "IN" else -t.amount

    series: list[tuple[date, Decimal]] = []
    current_day = start
    while current_day <= end:
        running = _q(running + by_day.get(current_day, Decimal("0")))
        series.append((current_day, running))
        current_day += timedelta(days=1)
    return series


def compute_summary(
    starting_cash: Decimal,
    transactions: list[Transaction],
    invoices: list[Invoice],
    recurring: list[RecurringObligation],
    as_of: date,
) -> FinancialSummary:
    cash = current_liquidity(starting_cash, transactions, as_of)
    inflow_30, outflow_30, net_30 = net_cash_flow(transactions, as_of - timedelta(days=30), as_of)
    burn = monthly_burn_rate(transactions, as_of)
    runway = cash_runway_days(cash, burn)
    receivables = outstanding_receivables(invoices, as_of)
    payables = outstanding_payables(invoices, as_of)
    overdue_recv_count, overdue_recv_amount = overdue_invoices(invoices, as_of, "RECEIVABLE")
    overdue_pay_count, overdue_pay_amount = overdue_invoices(invoices, as_of, "PAYABLE")
    upcoming = upcoming_obligations(recurring, invoices, as_of)
    concentration = concentration_risk(invoices)
    trend = expense_trend_pct(transactions, as_of)
    risk_level, reasons = classify_risk(cash, runway, overdue_recv_amount, concentration)

    return FinancialSummary(
        as_of=as_of,
        current_cash=cash,
        trailing_30d_inflow=inflow_30,
        trailing_30d_outflow=outflow_30,
        net_cash_flow_30d=net_30,
        monthly_burn_rate=burn,
        cash_runway_days=runway,
        outstanding_receivables=receivables,
        outstanding_payables=payables,
        overdue_receivables_count=overdue_recv_count,
        overdue_receivables_amount=overdue_recv_amount,
        overdue_payables_count=overdue_pay_count,
        overdue_payables_amount=overdue_pay_amount,
        upcoming_obligations_30d=upcoming,
        largest_customer_share_pct=concentration,
        expense_trend_pct=trend,
        risk_level=risk_level,
        risk_reasons=reasons,
    )
