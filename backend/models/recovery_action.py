"""Recovery Action model — an executed or proposed recovery action."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recovery_opportunities.id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    action_cost_paise: Mapped[int] = mapped_column(Integer, default=0)
    discount_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount_paise: Mapped[int] = mapped_column(Integer, default=0)
    razorpay_payment_link_id: Mapped[str | None] = mapped_column(String(100))
    execution_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    opportunity = relationship("RecoveryOpportunity", back_populates="actions")
    outcomes = relationship("RecoveryOutcome", back_populates="action")
    approvals = relationship("Approval", back_populates="action")
