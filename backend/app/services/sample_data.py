"""Six months of transactions, invoices and recurring obligations for an
e-commerce/retail business (the Northstar Studio dataset). Used by
scripts/seed_demo.py and by onboarding's "load sample data" option."""
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.financial import Invoice, RecurringObligation, Transaction
from app.models.organization import BusinessProfile

# Opening balance before the first transaction; the engine replays all
# transactions on top of it to reach today's cash position.
SAMPLE_OPENING_BALANCE = Decimal("5000.00")

SAMPLE_PROFILE = {
    "monthly_revenue_estimate": Decimal("14600.00"),
    "monthly_fixed_expenses_estimate": Decimal("11100.00"),
    "customer_payment_delay_days": 35,
    "supplier_payment_delay_days": 20,
    "employee_count": 8,
}


def seed_transactions(db: Session, org_id: str, as_of: date) -> None:
    for month_offset in range(6, 0, -1):
        month_anchor = as_of - timedelta(days=month_offset * 30)

        for day_offset, amount, customer in [
            (2, Decimal("6000.00"), "Atlas Retail Group"),
            (9, Decimal("4200.00"), "Bramble & Co"),
            (16, Decimal("2600.00"), "Coastal Supplies"),
            (23, Decimal("1800.00"), "Dune Market"),
        ]:
            db.add(
                Transaction(
                    organization_id=org_id,
                    date=month_anchor + timedelta(days=day_offset),
                    amount=amount,
                    currency="EUR",
                    category="sales_revenue",
                    direction="IN",
                    source="seed",
                    status="posted",
                    description=f"Payment received from {customer}",
                )
            )

        for day_offset, amount, category, description in [
            (1, Decimal("450.00"), "software", "Monthly software subscriptions"),
            (5, Decimal("2000.00"), "rent", "Office and warehouse rent"),
            (14, Decimal("650.00"), "operations", "Packaging and shipping supplies"),
            (21, Decimal("580.00"), "operations", "Marketing spend"),
            (28, Decimal("8000.00"), "payroll", "Monthly payroll run"),
        ]:
            db.add(
                Transaction(
                    organization_id=org_id,
                    date=month_anchor + timedelta(days=day_offset),
                    amount=amount,
                    currency="EUR",
                    category=category,
                    direction="OUT",
                    source="seed",
                    status="posted",
                    description=description,
                )
            )

    # Two one-off payments in the period: an equipment fit-out and the quarterly VAT.
    for days_ago, amount, category, description in [
        (120, Decimal("9500.00"), "equipment", "Warehouse shelving and packing station fit-out"),
        (45, Decimal("6000.00"), "tax", "Quarterly VAT payment"),
    ]:
        db.add(
            Transaction(
                organization_id=org_id,
                date=as_of - timedelta(days=days_ago),
                amount=amount,
                currency="EUR",
                category=category,
                direction="OUT",
                source="seed",
                status="posted",
                description=description,
            )
        )
    db.commit()


def seed_invoices(db: Session, org_id: str, as_of: date) -> None:
    receivables = [
        ("Atlas Retail Group", Decimal("3200.00"), -35, -5),
        ("Bramble & Co", Decimal("2150.00"), -40, -10),
        ("Coastal Supplies", Decimal("1800.00"), -50, -20),
        ("Dune Market", Decimal("2600.00"), -10, 8),
        ("Harbor Goods", Decimal("2400.00"), -5, 15),
        ("Atlas Retail Group", Decimal("9000.00"), -2, 40),
    ]
    payables = [
        ("Northwind Wholesale (Inventory)", Decimal("9500.00"), -1, 18),
        ("Pine Logistics", Decimal("1200.00"), -3, 12),
    ]
    for direction, rows, prefix in [("RECEIVABLE", receivables, "R"), ("PAYABLE", payables, "P")]:
        for name, amount, issue_offset, due_offset in rows:
            db.add(
                Invoice(
                    organization_id=org_id,
                    direction=direction,
                    counterparty_name=name,
                    amount=amount,
                    amount_paid=Decimal("0"),
                    currency="EUR",
                    issue_date=as_of + timedelta(days=issue_offset),
                    due_date=as_of + timedelta(days=due_offset),
                    status="unpaid",
                    reference=f"INV-{prefix}-{abs(due_offset):03d}-{name[:3].upper()}",
                )
            )
    db.commit()


def seed_recurring(db: Session, org_id: str, as_of: date) -> None:
    for name, amount, next_due_offset, category in [
        ("Office & warehouse rent", Decimal("2000.00"), 5, "rent"),
        ("Monthly payroll", Decimal("8000.00"), 10, "payroll"),
        ("Software subscriptions", Decimal("450.00"), 1, "software"),
    ]:
        db.add(
            RecurringObligation(
                organization_id=org_id,
                name=name,
                amount=amount,
                category=category,
                frequency="monthly",
                next_due_date=as_of + timedelta(days=next_due_offset),
                direction="OUT",
            )
        )
    db.commit()


def load_sample_data(db: Session, org_id: str, as_of: date) -> None:
    profile = db.query(BusinessProfile).filter(BusinessProfile.organization_id == org_id).first()
    if profile is None:
        profile = BusinessProfile(organization_id=org_id)
        db.add(profile)
    profile.current_cash_balance = SAMPLE_OPENING_BALANCE
    for field, value in SAMPLE_PROFILE.items():
        setattr(profile, field, value)
    db.commit()

    seed_transactions(db, org_id, as_of)
    seed_invoices(db, org_id, as_of)
    seed_recurring(db, org_id, as_of)
