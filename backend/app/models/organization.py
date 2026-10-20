from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import IDMixin, TimestampMixin


class Organization(Base, IDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(64), default="other")
    country: Mapped[str] = mapped_column(String(64), default="")
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    company_size: Mapped[str] = mapped_column(String(32), default="1-10")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    is_demo: Mapped[bool] = mapped_column(default=False)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="organization")
    business_profile: Mapped["BusinessProfile | None"] = relationship(
        back_populates="organization", uselist=False
    )


class BusinessProfile(Base, IDMixin, TimestampMixin):
    __tablename__ = "business_profiles"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), unique=True, nullable=False
    )
    monthly_revenue_estimate: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    monthly_fixed_expenses_estimate: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    current_cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    customer_payment_delay_days: Mapped[int] = mapped_column(default=30)
    supplier_payment_delay_days: Mapped[int] = mapped_column(default=30)
    employee_count: Mapped[int] = mapped_column(default=0)
    payroll_frequency: Mapped[str] = mapped_column(String(16), default="monthly")
    risk_tolerance: Mapped[str] = mapped_column(String(16), default="balanced")
    alert_sensitivity: Mapped[str] = mapped_column(String(16), default="balanced")
    forecast_horizon_days: Mapped[int] = mapped_column(default=90)

    organization: Mapped["Organization"] = relationship(back_populates="business_profile")


class OnboardingProgress(Base, IDMixin, TimestampMixin):
    __tablename__ = "onboarding_progress"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), unique=True, nullable=False
    )
    current_step: Mapped[int] = mapped_column(default=1)
    completed: Mapped[bool] = mapped_column(default=False)
    data_json: Mapped[str] = mapped_column(String, default="{}")
