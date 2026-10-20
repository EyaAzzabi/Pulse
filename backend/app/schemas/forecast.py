from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class ForecastRunRequest(BaseModel):
    horizon_days: int = 90


class ForecastPointOut(BaseModel):
    date: date
    projected_cash: Decimal
    known_component: Decimal
    uncertain_component: Decimal
    confidence: str


class ForecastRunOut(BaseModel):
    id: str
    created_at: datetime
    horizon_days: int
    method: str
    starting_cash: Decimal
    shortfall_date: date | None
    points: list[ForecastPointOut]
