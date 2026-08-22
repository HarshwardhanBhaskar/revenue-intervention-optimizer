"""Policy model — merchant-configured financial controls."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class MerchantPolicy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    max_automated_amount_paise: Mapped[int] = mapped_column(
        Integer, default=1_000_000  # ₹10,000
    )
    max_discount_percentage: Mapped[float] = mapped_column(
        Float, default=5.0
    )
    max_retry_attempts: Mapped[int] = mapped_column(
        Integer, default=2
    )
    min_incremental_value_paise: Mapped[int] = mapped_column(
        Integer, default=10_000  # ₹100
    )
    human_approval_threshold_paise: Mapped[int] = mapped_column(
        Integer, default=1_000_000  # ₹10,000
    )
    min_contact_interval_hours: Mapped[int] = mapped_column(
        Integer, default=24
    )
    enforce_opt_out: Mapped[bool] = mapped_column(Boolean, default=True)
    block_disputed: Mapped[bool] = mapped_column(Boolean, default=True)
    block_fraud_signals: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    merchant = relationship("Merchant", back_populates="policies")
