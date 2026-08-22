"""
Audit Engine — Immutable, append-only financial audit trail.

Records every state transition, policy check, AI recommendation,
human approval, and execution event with causal metadata.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_event import AuditEvent
from events.event_types import EventType, WorkflowState


class AuditEngine:
    """Manages append-only immutable audit logging."""

    @staticmethod
    async def log_event(
        db: AsyncSession,
        merchant_id: uuid.UUID,
        event_type: EventType | str,
        actor: str = "system",
        workflow_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        previous_state: Optional[WorkflowState | str] = None,
        new_state: Optional[WorkflowState | str] = None,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Create and persist an append-only audit event.
        Never updates or deletes records.
        """
        event = AuditEvent(
            id=uuid.uuid4(),
            merchant_id=merchant_id,
            workflow_id=workflow_id,
            event_type=event_type.value if isinstance(event_type, EventType) else str(event_type),
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_state=previous_state.value if isinstance(previous_state, WorkflowState) else str(previous_state) if previous_state else None,
            new_state=new_state.value if isinstance(new_state, WorkflowState) else str(new_state) if new_state else None,
            reason=reason,
            metadata_json=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        await db.flush()
        return event
