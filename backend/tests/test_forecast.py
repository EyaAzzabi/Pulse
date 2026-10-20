from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.forecasting.engine import find_shortfall, run_forecast

AS_OF = date(2026, 1, 1)


def inv(direction, amount, due_offset, status="unpaid"):
    due = AS_OF + timedelta(days=due_offset)
    return SimpleNamespace(direction=direction, amount=Decimal(amount), amount_paid=Decimal("0"), due_date=due, status=status)


def recurring(amount, next_due_offset, direction="OUT", frequency="monthly"):
    return SimpleNamespace(
        name="test",
        amount=Decimal(amount),
        category="test",
        frequency=frequency,
        next_due_date=AS_OF + timedelta(days=next_due_offset),
        direction=direction,
    )


def test_forecast_is_deterministic_for_same_inputs():
    invoices = [inv("PAYABLE", "500.00", 10)]
    points_1 = run_forecast(Decimal("1000"), [], invoices, [], AS_OF, 30)
    points_2 = run_forecast(Decimal("1000"), [], invoices, [], AS_OF, 30)
    assert [p.projected_cash for p in points_1] == [p.projected_cash for p in points_2]


def test_known_component_reflects_payable_due_date():
    invoices = [inv("PAYABLE", "500.00", 10)]
    points = run_forecast(Decimal("1000"), [], invoices, [], AS_OF, 30)
    day_10 = next(p for p in points if p.date == AS_OF + timedelta(days=10))
    assert day_10.known_component == Decimal("-500.00")


def test_receivable_due_date_is_known_inflow():
    invoices = [inv("RECEIVABLE", "300.00", 7)]
    points = run_forecast(Decimal("1000"), [], invoices, [], AS_OF, 30)
    day_7 = next(p for p in points if p.date == AS_OF + timedelta(days=7))
    assert day_7.known_component == Decimal("300.00")


def test_shortfall_detected_when_obligations_exceed_cash():
    invoices = [inv("PAYABLE", "5000.00", 5)]
    points = run_forecast(Decimal("1000"), [], invoices, [], AS_OF, 30)
    shortfall = find_shortfall(points)
    assert shortfall is not None
    assert shortfall.date == AS_OF + timedelta(days=5)
    assert shortfall.projected_cash < 0


def test_no_shortfall_with_ample_cash():
    invoices = [inv("PAYABLE", "100.00", 5)]
    points = run_forecast(Decimal("10000"), [], invoices, [], AS_OF, 30)
    assert find_shortfall(points) is None


def test_low_confidence_without_sufficient_history():
    points = run_forecast(Decimal("1000"), [], [], [], AS_OF, 60)
    assert all(p.confidence == "low" for p in points)


def test_forecast_starts_from_todays_cash_not_opening_balance():
    history = [SimpleNamespace(date=AS_OF - timedelta(days=10), amount=Decimal("5000.00"), direction="IN", category="sales")]
    points = run_forecast(Decimal("1000"), history, [], [], AS_OF, 5)
    assert points[0].projected_cash == Decimal("6000.00")
