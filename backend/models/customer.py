"""Customer model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    segment: Mapped[str] = mapped_column(String(50), nullable=False)  # premium, regular, price_sensitive, loyal, new
    historical_orders: Mapped[int] = mapped_column(Integer, default=0)
    successful_payments: Mapped[int] = mapped_column(Integer, default=0)
    failed_payments: Mapped[int] = mapped_column(Integer, default=0)
    historical_recovery_rate: Mapped[float] = mapped_column(Float, default=0.0)
    communication_preference: Mapped[str] = mapped_column(
        String(50), default="email"
    )  # email, sms, whatsapp
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False)
    has_active_dispute: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    orders = relationship("Order", back_populates="customer")
    recovery_opportunities = relationship("RecoveryOpportunity", back_populates="customer")
