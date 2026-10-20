from datetime import date as Date
from decimal import Decimal

from sqlalchemy import Date as SA_Date
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import IDMixin, TimestampMixin


class Transaction(Base, IDMixin, TimestampMixin):
    __tablename__ = "transactions"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    date: Mapped[Date] = mapped_column(SA_Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)  # IN | OUT
    source: Mapped[str] = mapped_column(String(32), default="seed")  # seed | csv_import | manual
    status: Mapped[str] = mapped_column(String(16), default="posted")
    description: Mapped[str] = mapped_column(String(255), default="")
    import_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)


class Invoice(Base, IDMixin, TimestampMixin):
    __tablename__ = "invoices"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # RECEIVABLE | PAYABLE
    counterparty_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    issue_date: Mapped[Date] = mapped_column(SA_Date, nullable=False)
    due_date: Mapped[Date] = mapped_column(SA_Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), default="unpaid")  # unpaid | paid | overdue | partial
    reference: Mapped[str] = mapped_column(String(64), default="")


class RecurringObligation(Base, IDMixin, TimestampMixin):
    __tablename__ = "recurring_obligations"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="operating")
    frequency: Mapped[str] = mapped_column(String(16), default="monthly")  # monthly | weekly
    next_due_date: Mapped[Date] = mapped_column(SA_Date, nullable=False)
    direction: Mapped[str] = mapped_column(String(8), default="OUT")
