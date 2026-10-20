from decimal import Decimal

from pydantic import BaseModel


class OrganizationOut(BaseModel):
    id: str
    name: str
    industry: str
    country: str
    currency: str
    company_size: str
    timezone: str
    is_demo: bool
    role: str

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    country: str | None = None
    currency: str | None = None
    company_size: str | None = None
    timezone: str | None = None


class MemberOut(BaseModel):
    user_id: str
    full_name: str
    email: str
    role: str


class BusinessProfileOut(BaseModel):
    monthly_revenue_estimate: Decimal
    monthly_fixed_expenses_estimate: Decimal
    current_cash_balance: Decimal
    customer_payment_delay_days: int
    supplier_payment_delay_days: int
    employee_count: int
    payroll_frequency: str
    risk_tolerance: str
    alert_sensitivity: str
    forecast_horizon_days: int

    class Config:
        from_attributes = True


class BusinessProfileUpdate(BaseModel):
    monthly_revenue_estimate: Decimal | None = None
    monthly_fixed_expenses_estimate: Decimal | None = None
    current_cash_balance: Decimal | None = None
    customer_payment_delay_days: int | None = None
    supplier_payment_delay_days: int | None = None
    employee_count: int | None = None
    payroll_frequency: str | None = None
    risk_tolerance: str | None = None
    alert_sensitivity: str | None = None
    forecast_horizon_days: int | None = None
