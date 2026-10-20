from datetime import date as Date
from decimal import Decimal

from sqlalchemy import Date as SA_Date
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import IDMixin, TimestampMixin


class ForecastRun(Base, IDMixin, TimestampMixin):
    __tablename__ = "forecast_runs"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    horizon_days: Mapped[int] = mapped_column(default=90)
    method: Mapped[str] = mapped_column(String(32), default="deterministic_baseline")
    assumptions_json: Mapped[str] = mapped_column(Text, default="{}")
    starting_cash: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    points: Mapped[list["ForecastPoint"]] = relationship(
        back_populates="forecast_run", cascade="all, delete-orphan"
    )


class ForecastPoint(Base, IDMixin, TimestampMixin):
    __tablename__ = "forecast_points"

    forecast_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("forecast_runs.id"), index=True)
    date: Mapped[Date] = mapped_column(SA_Date, nullable=False, index=True)
    projected_cash: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    known_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    uncertain_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    confidence: Mapped[str] = mapped_column(String(16), default="medium")  # high | medium | low

    forecast_run: Mapped["ForecastRun"] = relationship(back_populates="points")
