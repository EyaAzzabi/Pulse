from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import IDMixin, TimestampMixin


class SimulationScenario(Base, IDMixin, TimestampMixin):
    __tablename__ = "simulation_scenarios"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    created_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), default="Untitled scenario")
    assumptions_json: Mapped[str] = mapped_column(Text, default="{}")

    result: Mapped["SimulationResult | None"] = relationship(
        back_populates="scenario", uselist=False, cascade="all, delete-orphan"
    )


class SimulationResult(Base, IDMixin, TimestampMixin):
    __tablename__ = "simulation_results"

    scenario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("simulation_scenarios.id"), unique=True, index=True
    )
    lowest_cash_point: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    lowest_cash_date: Mapped[str] = mapped_column(String(32), default="")
    runway_days: Mapped[int | None] = mapped_column(nullable=True)
    days_below_zero: Mapped[int] = mapped_column(default=0)
    impact_vs_baseline_json: Mapped[str] = mapped_column(Text, default="{}")
    baseline_points_json: Mapped[str] = mapped_column(Text, default="[]")
    simulated_points_json: Mapped[str] = mapped_column(Text, default="[]")

    scenario: Mapped["SimulationScenario"] = relationship(back_populates="result")


class Recommendation(Base, IDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, default="")
    expected_impact: Mapped[str] = mapped_column(Text, default="")
    risk_level: Mapped[str] = mapped_column(String(16), default="medium")  # low | medium | high
    requires_approval: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(32), default="proposed")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")


class ActionProposal(Base, IDMixin, TimestampMixin):
    __tablename__ = "action_proposals"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    created_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. send_invoice_reminder
    target_json: Mapped[str] = mapped_column(Text, default="{}")
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    risks: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    requires_approval: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(32), default="pending_approval")
    # DRAFT, PENDING_APPROVAL, APPROVED, QUEUED, SENT, FAILED, CANCELLED
    approved_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    execution_result_json: Mapped[str] = mapped_column(Text, default="{}")
