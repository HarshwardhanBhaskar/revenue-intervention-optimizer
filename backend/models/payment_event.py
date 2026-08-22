"""Payment Event model — webhook event deduplication."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payments.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    razorpay_event_id: Mapped[str | None] = mapped_column(String(200))
    payload: Mapped[dict | None] = mapped_column(JSON)
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    payment = relationship("Payment", back_populates="events")

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_payment_events_idempotency"),
    )
