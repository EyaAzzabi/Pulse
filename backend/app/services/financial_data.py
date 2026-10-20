from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.financial import Invoice, RecurringObligation, Transaction
from app.models.organization import BusinessProfile


def load_financial_inputs(db: Session, organization_id: str):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.organization_id == organization_id)
        .order_by(Transaction.date)
        .all()
    )
    invoices = db.query(Invoice).filter(Invoice.organization_id == organization_id).all()
    recurring = (
        db.query(RecurringObligation).filter(RecurringObligation.organization_id == organization_id).all()
    )
    profile = (
        db.query(BusinessProfile).filter(BusinessProfile.organization_id == organization_id).first()
    )
    starting_cash = profile.current_cash_balance if profile else Decimal("0")
    return starting_cash, transactions, invoices, recurring


def refresh_overdue_status(db: Session, organization_id: str, as_of: date) -> None:
    """Keep invoice.status consistent with due_date vs as_of. Idempotent."""
    invoices = db.query(Invoice).filter(Invoice.organization_id == organization_id).all()
    changed = False
    for inv in invoices:
        remaining = inv.amount - inv.amount_paid
        if remaining <= 0 and inv.status != "paid":
            inv.status = "paid"
            changed = True
        elif remaining > 0 and inv.due_date < as_of and inv.status not in ("overdue",):
            inv.status = "overdue"
            changed = True
        elif remaining > 0 and inv.due_date >= as_of and inv.status == "overdue":
            inv.status = "unpaid"
            changed = True
    if changed:
        db.commit()
