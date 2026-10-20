from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.financial.engine import (
    cash_runway_days,
    classify_risk,
    compute_summary,
    concentration_risk,
    current_liquidity,
    net_cash_flow,
    outstanding_receivables,
    overdue_invoices,
)

TODAY = date(2026, 1, 30)


def tx(d, amount, direction):
    return SimpleNamespace(date=d, amount=Decimal(amount), direction=direction)


def inv(direction, amount, amount_paid, due_date, status, counterparty="Customer"):
    return SimpleNamespace(
        direction=direction,
        amount=Decimal(amount),
        amount_paid=Decimal(amount_paid),
        due_date=due_date,
        status=status,
        counterparty_name=counterparty,
    )


def test_current_liquidity_is_conservative():
    transactions = [
        tx(TODAY - timedelta(days=10), "1000.00", "IN"),
        tx(TODAY - timedelta(days=5), "300.00", "OUT"),
    ]
    cash = current_liquidity(Decimal("500.00"), transactions, TODAY)
    assert cash == Decimal("1200.00")


def test_net_cash_flow_matches_inflow_minus_outflow():
    transactions = [
        tx(TODAY, "500.00", "IN"),
        tx(TODAY, "200.00", "OUT"),
    ]
    inflow, outflow, net = net_cash_flow(transactions, TODAY, TODAY)
    assert inflow == Decimal("500.00")
    assert outflow == Decimal("200.00")
    assert net == Decimal("300.00")


def test_cash_runway_none_when_not_burning():
    assert cash_runway_days(Decimal("1000"), Decimal("0")) is None
    assert cash_runway_days(Decimal("1000"), Decimal("-50")) is None


def test_cash_runway_days_computation():
    # 3000 cash, burning 300/month -> 10/day -> 300 days
    assert cash_runway_days(Decimal("3000"), Decimal("300")) == 300


def test_outstanding_receivables_excludes_paid():
    invoices = [
        inv("RECEIVABLE", "100.00", "0", TODAY, "unpaid"),
        inv("RECEIVABLE", "50.00", "50.00", TODAY, "paid"),
        inv("PAYABLE", "999.00", "0", TODAY, "unpaid"),
    ]
    assert outstanding_receivables(invoices, TODAY) == Decimal("100.00")


def test_overdue_invoices_counts_only_past_due_unpaid():
    invoices = [
        inv("RECEIVABLE", "100.00", "0", TODAY - timedelta(days=5), "unpaid"),
        inv("RECEIVABLE", "200.00", "0", TODAY + timedelta(days=5), "unpaid"),
        inv("RECEIVABLE", "300.00", "300.00", TODAY - timedelta(days=5), "paid"),
    ]
    count, total = overdue_invoices(invoices, TODAY, "RECEIVABLE")
    assert count == 1
    assert total == Decimal("100.00")


def test_concentration_risk_single_customer_is_100_pct():
    invoices = [
        inv("RECEIVABLE", "100.00", "0", TODAY, "unpaid", counterparty="Only Customer"),
    ]
    assert concentration_risk(invoices) == Decimal("100.00")


def test_concentration_risk_zero_when_no_outstanding():
    assert concentration_risk([]) == Decimal("0.00")


def test_classify_risk_flags_negative_cash():
    level, reasons = classify_risk(Decimal("-100"), None, Decimal("0"), Decimal("0"))
    assert level == "high"
    assert any("negative" in r for r in reasons)


def test_classify_risk_low_when_healthy():
    level, reasons = classify_risk(Decimal("10000"), 400, Decimal("0"), Decimal("10"))
    assert level == "low"


def test_compute_summary_is_reproducible():
    transactions = [tx(TODAY - timedelta(days=1), "1000.00", "IN")]
    invoices = [inv("RECEIVABLE", "200.00", "0", TODAY + timedelta(days=5), "unpaid")]
    recurring = []

    summary_1 = compute_summary(Decimal("500.00"), transactions, invoices, recurring, TODAY)
    summary_2 = compute_summary(Decimal("500.00"), transactions, invoices, recurring, TODAY)

    assert summary_1.current_cash == summary_2.current_cash
    assert summary_1.risk_level == summary_2.risk_level
    assert summary_1.current_cash == Decimal("1500.00")
