"""Merchant model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    razorpay_account_id: Mapped[str | None] = mapped_column(String(100))
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    customers = relationship("Customer", back_populates="merchant")
    policies = relationship("MerchantPolicy", back_populates="merchant")
    experiments = relationship("Experiment", back_populates="merchant")
    audit_events = relationship("AuditEvent", back_populates="merchant")
