"""Model Prediction model — logged ML predictions for audit + analysis."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recovery_opportunities.id"), nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    feature_importances: Mapped[dict | None] = mapped_column(JSON)
    inference_latency_ms: Mapped[float | None] = mapped_column(Float)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    opportunity = relationship("RecoveryOpportunity", back_populates="predictions")
