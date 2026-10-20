from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.simulations.engine import ScenarioAssumptions, run_simulation

AS_OF = date(2026, 1, 1)


def inv(direction, amount, due_offset, status="unpaid"):
    due = AS_OF + timedelta(days=due_offset)
    return SimpleNamespace(direction=direction, amount=Decimal(amount), amount_paid=Decimal("0"), due_date=due, status=status)


def test_simulation_does_not_mutate_input_invoices():
    receivable = inv("RECEIVABLE", "1000.00", 10)
    original_due_date = receivable.due_date

    run_simulation(
        Decimal("500"), [], [receivable], [], AS_OF, 30, ScenarioAssumptions(customer_payment_delay_days=20)
    )

    assert receivable.due_date == original_due_date


def test_customer_delay_worsens_lowest_cash_point():
    receivable = inv("RECEIVABLE", "1000.00", 5)
    payable = inv("PAYABLE", "900.00", 6)

    baseline = run_simulation(Decimal("500"), [], [receivable, payable], [], AS_OF, 30, ScenarioAssumptions())
    delayed = run_simulation(
        Decimal("500"), [], [receivable, payable], [], AS_OF, 30,
        ScenarioAssumptions(customer_payment_delay_days=15),
    )

    assert delayed.lowest_cash_point <= baseline.lowest_cash_point


def test_one_time_cash_injection_improves_lowest_point():
    payable = inv("PAYABLE", "900.00", 3)

    baseline = run_simulation(Decimal("500"), [], [payable], [], AS_OF, 30, ScenarioAssumptions())
    injected = run_simulation(
        Decimal("500"), [], [payable], [], AS_OF, 30,
        ScenarioAssumptions(one_time_cash_injection=Decimal("2000")),
    )

    assert injected.lowest_cash_point > baseline.lowest_cash_point


def test_two_identical_scenarios_produce_identical_results():
    payable = inv("PAYABLE", "900.00", 3)
    a = run_simulation(Decimal("500"), [], [payable], [], AS_OF, 30, ScenarioAssumptions(expense_change_pct=Decimal("-10")))
    b = run_simulation(Decimal("500"), [], [payable], [], AS_OF, 30, ScenarioAssumptions(expense_change_pct=Decimal("-10")))
    assert a.lowest_cash_point == b.lowest_cash_point
    assert a.days_below_zero == b.days_below_zero


def test_simulation_starts_from_todays_cash():
    history = [SimpleNamespace(date=AS_OF - timedelta(days=10), amount=Decimal("5000.00"), direction="IN", category="sales")]
    out = run_simulation(Decimal("1000"), history, [], [], AS_OF, 5, ScenarioAssumptions())
    assert out.simulated_points[0].projected_cash == Decimal("6000.00")
    assert out.baseline_points[0].projected_cash == Decimal("6000.00")


def test_customer_delay_can_target_one_customer():
    atlas = SimpleNamespace(direction="RECEIVABLE", amount=Decimal("1000"), amount_paid=Decimal("0"),
                            due_date=AS_OF + timedelta(days=5), status="unpaid", counterparty_name="Atlas Retail Group")
    other = SimpleNamespace(direction="RECEIVABLE", amount=Decimal("500"), amount_paid=Decimal("0"),
                            due_date=AS_OF + timedelta(days=5), status="unpaid", counterparty_name="Bramble & Co")
    out = run_simulation(Decimal("0"), [], [atlas, other], [], AS_OF, 30,
                         ScenarioAssumptions(customer_payment_delay_days=10, delayed_customer="atlas"))
    day5 = next(p for p in out.simulated_points if p.date == AS_OF + timedelta(days=5))
    day15 = next(p for p in out.simulated_points if p.date == AS_OF + timedelta(days=15))
    assert day5.known_component == Decimal("500.00")
    assert day15.known_component == Decimal("1000.00")
