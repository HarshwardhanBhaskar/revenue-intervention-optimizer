"""Experiment Assignment model — maps opportunities to experiment groups."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("experiments.id"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recovery_opportunities.id"), nullable=False
    )
    group_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "control" or "treatment"
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    experiment = relationship("Experiment", back_populates="assignments")
    opportunity = relationship("RecoveryOpportunity", back_populates="experiment_assignments")
