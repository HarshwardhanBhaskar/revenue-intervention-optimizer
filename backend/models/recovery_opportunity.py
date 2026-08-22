"""Recovery Opportunity model — the core entity of the system."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Index, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class RecoveryOpportunity(Base):
    __tablename__ = "recovery_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payments.id"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)

    # Workflow state — managed by state machine
    workflow_state: Mapped[str] = mapped_column(
        String(50), default="detected", nullable=False
    )

    # AI recommendation
    recommended_action: Mapped[str | None] = mapped_column(String(50))
    baseline_probability: Mapped[float | None] = mapped_column(Float)
    recommended_probability: Mapped[float | None] = mapped_column(Float)
    expected_incremental_value_paise: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)

    # Context
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    feature_vector: Mapped[dict | None] = mapped_column(JSON)
    action_rankings: Mapped[dict | None] = mapped_column(JSON)

    # Policy + Risk results
    policy_result: Mapped[str | None] = mapped_column(String(50))
    risk_result: Mapped[str | None] = mapped_column(String(50))
    policy_checks: Mapped[dict | None] = mapped_column(JSON)
    risk_checks: Mapped[dict | None] = mapped_column(JSON)

    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    payment = relationship("Payment", back_populates="recovery_opportunities")
    customer = relationship("Customer", back_populates="recovery_opportunities")
    actions = relationship("RecoveryAction", back_populates="opportunity")
    outcomes = relationship("RecoveryOutcome", back_populates="opportunity")
    predictions = relationship("ModelPrediction", back_populates="opportunity")
    experiment_assignments = relationship("ExperimentAssignment", back_populates="opportunity")

    __table_args__ = (
        Index("idx_opportunities_state", "workflow_state"),
        Index("idx_opportunities_detected", "detected_at"),
    )
