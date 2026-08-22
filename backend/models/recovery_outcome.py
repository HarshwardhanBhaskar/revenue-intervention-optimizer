"""Recovery Outcome model — the observed result of a recovery action."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    action_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recovery_actions.id"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recovery_opportunities.id"), nullable=False
    )
    payment_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recovered_amount_paise: Mapped[int] = mapped_column(Integer, default=0)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(100))
    customer_response: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    action = relationship("RecoveryAction", back_populates="outcomes")
    opportunity = relationship("RecoveryOpportunity", back_populates="outcomes")
