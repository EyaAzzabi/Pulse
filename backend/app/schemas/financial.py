from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FinancialSummaryOut(BaseModel):
    as_of: date
    currency: str
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
    risk_reasons: list[str]


class TransactionOut(BaseModel):
    id: str
    date: date
    amount: Decimal
    currency: str
    category: str
    direction: str
    source: str
    status: str
    description: str

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: str
    direction: str
    counterparty_name: str
    amount: Decimal
    amount_paid: Decimal
    currency: str
    issue_date: date
    due_date: date
    status: str
    reference: str

    class Config:
        from_attributes = True


class CashflowPointOut(BaseModel):
    date: date
    actual_cash: Decimal | None = None
    projected_cash: Decimal | None = None
    confidence: str | None = None
    is_forecast: bool
