"""
Recovery Opportunities API — Listing, Details, and Counterfactual Simulations.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from models.database import get_db
from models.recovery_opportunity import RecoveryOpportunity
from models.customer import Customer
from models.payment import Payment
from domain.decision_engine import DecisionEngine, ActionType
from domain.policy_engine import PolicyEngine, PolicyConfig, RecoveryContext, RecommendedAction

router = APIRouter()
decision_engine = DecisionEngine()


@router.get("")
async def list_opportunities(
    status: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    amount_min: Optional[int] = Query(None),
    amount_max: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List recovery opportunities with filters and pagination."""
    stmt = (
        select(RecoveryOpportunity)
        .options(
            selectinload(RecoveryOpportunity.customer),
            selectinload(RecoveryOpportunity.payment),
            selectinload(RecoveryOpportunity.actions),
            selectinload(RecoveryOpportunity.outcomes),
        )
        .order_by(desc(RecoveryOpportunity.detected_at))
    )

    if status:
        stmt = stmt.where(RecoveryOpportunity.workflow_state == status)
    if action:
        stmt = stmt.where(RecoveryOpportunity.recommended_action == action)
    if amount_min:
        stmt = stmt.where(RecoveryOpportunity.amount_paise >= amount_min)
    if amount_max:
        stmt = stmt.where(RecoveryOpportunity.amount_paise <= amount_max)

    offset = (page - 1) * per_page
    paginated_stmt = stmt.offset(offset).limit(per_page)

    res = await db.execute(paginated_stmt)
    opps = res.scalars().all()

    items = []
    for o in opps:
        items.append({
            "id": str(o.id),
            "amount_paise": o.amount_paise,
            "amount_rupees": o.amount_paise / 100.0,
            "workflow_state": o.workflow_state,
            "recommended_action": o.recommended_action,
            "baseline_probability": o.baseline_probability,
            "recommended_probability": o.recommended_probability,
            "expected_incremental_value_paise": o.expected_incremental_value_paise or 0,
            "confidence": o.confidence or 0.85,
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
            "policy_result": o.policy_result,
            "detected_at": o.detected_at.isoformat() if o.detected_at else None,
        })

    return {
        "opportunities": items,
        "page": page,
        "per_page": per_page,
        "total": len(items),  # simplified for pagination
    }


@router.get("/{opportunity_id}")
async def get_opportunity(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    """Get full details of a recovery opportunity."""
    try:
        u_id = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid opportunity ID format")

    stmt = (
        select(RecoveryOpportunity)
        .options(
            selectinload(RecoveryOpportunity.customer),
            selectinload(RecoveryOpportunity.payment),
            selectinload(RecoveryOpportunity.actions),
            selectinload(RecoveryOpportunity.outcomes),
        )
        .where(RecoveryOpportunity.id == u_id)
    )
    res = await db.execute(stmt)
    opp = res.scalars().first()

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return {
        "id": str(opp.id),
        "amount_paise": opp.amount_paise,
        "amount_rupees": opp.amount_paise / 100.0,
        "workflow_state": opp.workflow_state,
        "recommended_action": opp.recommended_action,
        "baseline_probability": opp.baseline_probability,
        "recommended_probability": opp.recommended_probability,
        "expected_incremental_value_paise": opp.expected_incremental_value_paise or 0,
        "confidence": opp.confidence or 0.85,
        "feature_vector": opp.feature_vector or {},
        "action_rankings": opp.action_rankings or {},
        "policy_result": opp.policy_result,
        "risk_result": opp.risk_result,
        "policy_checks": opp.policy_checks or {},
        "detected_at": opp.detected_at.isoformat() if opp.detected_at else None,
        "customer": {
            "id": str(opp.customer.id),
            "external_id": opp.customer.external_id,
            "segment": opp.customer.segment,
            "historical_orders": opp.customer.historical_orders,
            "historical_recovery_rate": opp.customer.historical_recovery_rate,
            "opted_out": opp.customer.opted_out,
            "has_active_dispute": opp.customer.has_active_dispute,
        } if opp.customer else None,
        "payment": {
            "id": str(opp.payment.id),
            "razorpay_payment_id": opp.payment.razorpay_payment_id,
            "payment_method": opp.payment.payment_method,
            "failure_reason": opp.payment.failure_reason,
            "created_at": opp.payment.created_at.isoformat() if opp.payment.created_at else None,
        } if opp.payment else None,
        "actions": [
            {
                "id": str(a.id),
                "action_type": a.action_type,
                "status": a.status,
                "action_cost_paise": a.action_cost_paise,
                "discount_percentage": a.discount_percentage,
                "razorpay_payment_link_id": a.razorpay_payment_link_id,
                "executed_at": a.executed_at.isoformat() if a.executed_at else None,
            }
            for a in opp.actions
        ],
        "outcomes": [
            {
                "id": str(oc.id),
                "payment_success": oc.payment_success,
                "recovered_amount_paise": oc.recovered_amount_paise,
                "observed_at": oc.observed_at.isoformat() if oc.observed_at else None,
            }
            for oc in opp.outcomes
        ],
    }


@router.post("/{opportunity_id}/simulate")
async def simulate_opportunity(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    """
    Decision Lab: Run counterfactual simulations comparing all 5 actions
    and multiple discount percentages.
    """
    try:
        u_id = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid opportunity ID format")

    stmt = select(RecoveryOpportunity).where(RecoveryOpportunity.id == u_id)
    res = await db.execute(stmt)
    opp = res.scalars().first()

    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    amt_paise = opp.amount_paise
    base_p = opp.baseline_probability or 0.30

    # Default action comparisons
    scenarios = [
        {"action": ActionType.DO_NOTHING, "prob": base_p, "cost": 0, "disc": 0.0},
        {"action": ActionType.RETRY, "prob": min(base_p + 0.20, 0.95), "cost": 1000, "disc": 0.0},
        {"action": ActionType.PAYMENT_LINK, "prob": min(base_p + 0.35, 0.95), "cost": 2000, "disc": 0.0},
        {"action": ActionType.REMINDER, "prob": min(base_p + 0.15, 0.95), "cost": 500, "disc": 0.0},
        {"action": ActionType.DISCOUNT, "prob": min(base_p + 0.42, 0.98), "cost": 2000, "disc": 5.0},
    ]

    results = []
    for sc in scenarios:
        econ = decision_engine.compute_action_economics(
            action_type=sc["action"],
            amount_paise=amt_paise,
            p_recovery=sc["prob"],
            p_baseline=base_p,
            discount_pct=sc["disc"],
        )
        results.append(econ.to_dict())

    # Sort descending by incremental net value
    results.sort(key=lambda x: x["incremental_value"], reverse=True)

    # What-if discount sensitivity
    discount_sensitivity = decision_engine.simulate_discount_scenarios(
        amount_paise=amt_paise,
        p_baseline=base_p,
        p_discount_base=min(base_p + 0.30, 0.95),
        discount_percentages=[2.0, 5.0, 8.0, 10.0],
    )

    return {
        "opportunity_id": opportunity_id,
        "amount_paise": amt_paise,
        "amount_rupees": amt_paise / 100.0,
        "baseline_probability": base_p,
        "action_comparisons": results,
        "recommended_action": results[0]["action_type"] if results else "do_nothing",
        "discount_sensitivity": [s.to_dict() for s in discount_sensitivity],
    }
