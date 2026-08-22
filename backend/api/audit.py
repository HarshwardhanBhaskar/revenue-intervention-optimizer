"""Audit API — Searchable and filterable event stream."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.database import get_db
from models.audit_event import AuditEvent

router = APIRouter()


@router.get("")
async def list_audit_events(
    event_type: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Query immutable audit events with pagination and filters."""
    stmt = select(AuditEvent).order_by(desc(AuditEvent.created_at))

    if event_type:
        stmt = stmt.where(AuditEvent.event_type == event_type)
    if workflow_id:
        try:
            u_id = uuid.UUID(workflow_id)
            stmt = stmt.where(AuditEvent.workflow_id == u_id)
        except ValueError:
            pass

    offset = (page - 1) * per_page
    paginated_stmt = stmt.offset(offset).limit(per_page)

    res = await db.execute(paginated_stmt)
    events = res.scalars().all()

    return {
        "events": [
            {
                "id": str(e.id),
                "workflow_id": str(e.workflow_id) if e.workflow_id else None,
                "event_type": e.event_type,
                "actor": e.actor,
                "entity_type": e.entity_type,
                "entity_id": str(e.entity_id) if e.entity_id else None,
                "previous_state": e.previous_state,
                "new_state": e.new_state,
                "reason": e.reason,
                "metadata": e.metadata_json or {},
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ],
        "page": page,
        "per_page": per_page,
    }
