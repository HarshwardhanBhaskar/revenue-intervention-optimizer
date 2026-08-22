"""Audit Event model — immutable, append-only audit trail."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("merchants.id"), nullable=False
    )
    workflow_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor: Mapped[str] = mapped_column(String(200), default="system")
    entity_type: Mapped[str | None] = mapped_column(String(100))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    previous_state: Mapped[str | None] = mapped_column(String(100))
    new_state: Mapped[str | None] = mapped_column(String(100))
    reason: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    merchant = relationship("Merchant", back_populates="audit_events")

    __table_args__ = (
        Index("idx_audit_workflow", "workflow_id", "created_at"),
        Index("idx_audit_type", "event_type", "created_at"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
    )
