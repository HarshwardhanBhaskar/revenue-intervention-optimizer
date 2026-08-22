"""Actions API — Approve/Reject high-value human escalations & list pending queue."""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from models.database import get_db
from models.recovery_opportunity import RecoveryOpportunity
from models.recovery_action import RecoveryAction
from models.customer import Customer
from models.payment import Payment
from domain.audit_engine import AuditEngine
from domain.recovery_engine import RecoveryEngine
from events.event_types import WorkflowState, EventType

router = APIRouter()
recovery_engine = RecoveryEngine()


@router.get("/pending")
async def list_pending_actions(db: AsyncSession = Depends(get_db)):
    """List all high-value transactions awaiting human operator approval."""
    stmt = (
        select(RecoveryOpportunity)
        .options(
            selectinload(RecoveryOpportunity.customer),
            selectinload(RecoveryOpportunity.payment),
            selectinload(RecoveryOpportunity.actions),
        )
        .where(RecoveryOpportunity.workflow_state == WorkflowState.PENDING_APPROVAL.value)
        .order_by(desc(RecoveryOpportunity.amount_paise))
    )
    res = await db.execute(stmt)
    opps = res.scalars().all()

    items = []
    for o in opps:
        pending_action = o.actions[0] if o.actions else None
        items.append({
            "opportunity_id": str(o.id),
            "action_id": str(pending_action.id) if pending_action else None,
            "amount_paise": o.amount_paise,
            "amount_rupees": o.amount_paise / 100.0,
            "recommended_action": o.recommended_action,
            "baseline_probability": o.baseline_probability,
            "recommended_probability": o.recommended_probability,
            "expected_incremental_value_paise": o.expected_incremental_value_paise or 0,
            "confidence": o.confidence or 0.90,
            "customer": {
                "id": str(o.customer.id),
                "external_id": o.customer.external_id,
                "segment": o.customer.segment,
                "recovery_rate": o.customer.historical_recovery_rate,
            } if o.customer else None,
            "payment": {
                "id": str(o.payment.id),
                "method": o.payment.payment_method,
                "failure_reason": o.payment.failure_reason,
            } if o.payment else None,
            "detected_at": o.detected_at.isoformat() if o.detected_at else None,
        })

    return {"pending_actions": items, "count": len(items)}


@router.post("/{opportunity_id}/approve")
async def approve_action(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    """Approve a pending recovery action."""
    try:
        u_id = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    stmt = (
        select(RecoveryOpportunity)
        .options(
            selectinload(RecoveryOpportunity.customer),
            selectinload(RecoveryOpportunity.payment),
            selectinload(RecoveryOpportunity.actions),
        )
        .where(RecoveryOpportunity.id == u_id)
    )
    res = await db.execute(stmt)
    opp = res.scalars().first()

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if opp.workflow_state != WorkflowState.PENDING_APPROVAL.value:
        raise HTTPException(
            status_code=409,
            detail=f"Action is not in pending_approval state (current: {opp.workflow_state})"
        )

    # Log approval audit
    await AuditEngine.log_event(
        db=db,
        merchant_id=opp.customer.merchant_id,
        event_type=EventType.RECOVERY_APPROVED,
        actor="operator_human",
        workflow_id=opp.id,
        entity_type="recovery_opportunity",
        entity_id=opp.id,
        previous_state=WorkflowState.PENDING_APPROVAL,
        new_state=WorkflowState.APPROVED,
        reason="Approved by merchant revenue operations manager",
    )

    # Execute action
    opp.workflow_state = WorkflowState.APPROVED.value
    await db.flush()

    action = await recovery_engine.execute_approved_action(
        db=db,
        opportunity=opp,
        payment=opp.payment,
        customer=opp.customer,
        merchant_id=opp.customer.merchant_id,
    )
    await db.commit()

    return {
        "status": "approved",
        "opportunity_id": str(opp.id),
        "action_id": str(action.id),
        "workflow_state": opp.workflow_state,
        "payment_link": action.razorpay_payment_link_id,
    }


@router.post("/{opportunity_id}/reject")
async def reject_action(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    """Reject a pending recovery action."""
    try:
        u_id = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    stmt = select(RecoveryOpportunity).options(selectinload(RecoveryOpportunity.customer)).where(RecoveryOpportunity.id == u_id)
    res = await db.execute(stmt)
    opp = res.scalars().first()

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if opp.workflow_state != WorkflowState.PENDING_APPROVAL.value:
        raise HTTPException(
            status_code=409,
            detail=f"Action is not in pending_approval state (current: {opp.workflow_state})"
        )

    opp.workflow_state = WorkflowState.BLOCKED.value
    await db.flush()

    await AuditEngine.log_event(
        db=db,
        merchant_id=opp.customer.merchant_id,
        event_type=EventType.RECOVERY_REJECTED,
        actor="operator_human",
        workflow_id=opp.id,
        entity_type="recovery_opportunity",
        entity_id=opp.id,
        previous_state=WorkflowState.PENDING_APPROVAL,
        new_state=WorkflowState.BLOCKED,
        reason="Rejected by merchant operator — recovery stopped",
    )
    await db.commit()

    return {
        "status": "rejected",
        "opportunity_id": str(opp.id),
        "workflow_state": opp.workflow_state,
    }
