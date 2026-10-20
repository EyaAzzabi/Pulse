from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.forecast import ForecastPointOut


class SimulationCreateRequest(BaseModel):
    name: str = "Untitled scenario"
    horizon_days: int = 90
    customer_payment_delay_days: int = 0
    supplier_payment_delay_days: int = 0
    revenue_change_pct: Decimal = Decimal("0")
    expense_change_pct: Decimal = Decimal("0")
    inventory_purchase_amount: Decimal = Decimal("0")
    financing_amount: Decimal = Decimal("0")
    financing_monthly_cost: Decimal = Decimal("0")
    one_time_cash_injection: Decimal = Decimal("0")


class SimulationResultOut(BaseModel):
    id: str
    scenario_id: str
    name: str
    created_at: datetime
    assumptions: dict
    lowest_cash_point: Decimal
    lowest_cash_date: date | None
    runway_days: int | None
    days_below_zero: int
    impact_vs_baseline: Decimal
    baseline_points: list[ForecastPointOut]
    simulated_points: list[ForecastPointOut]


class SimulationListItemOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    lowest_cash_point: Decimal
    impact_vs_baseline: Decimal
