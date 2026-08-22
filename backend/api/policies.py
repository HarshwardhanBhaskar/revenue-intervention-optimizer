"""Policies API — Merchant Financial Controls Configuration."""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from models.database import get_db
from models.policy import MerchantPolicy
from models.merchant import Merchant
from domain.audit_engine import AuditEngine
from events.event_types import EventType

router = APIRouter()


class PolicyUpdateSchema(BaseModel):
    max_automated_amount_paise: Optional[int] = Field(None, ge=1000)
    max_discount_percentage: Optional[float] = Field(None, ge=0.0, le=25.0)
    max_retry_attempts: Optional[int] = Field(None, ge=0, le=5)
    min_incremental_value_paise: Optional[int] = Field(None, ge=0)
    human_approval_threshold_paise: Optional[int] = Field(None, ge=1000)
    min_contact_interval_hours: Optional[int] = Field(None, ge=1, le=168)
    enforce_opt_out: Optional[bool] = None
    block_disputed: Optional[bool] = None
    block_fraud_signals: Optional[bool] = None


@router.get("")
async def get_policy(db: AsyncSession = Depends(get_db)):
    """Get active merchant policy configuration."""
    stmt = select(MerchantPolicy).where(MerchantPolicy.is_active == True)
    res = await db.execute(stmt)
    policy = res.scalars().first()

    if not policy:
        # Create default if not present
        m_stmt = select(Merchant)
        merchant = (await db.execute(m_stmt)).scalars().first()
        m_id = merchant.id if merchant else uuid.uuid4()

        policy = MerchantPolicy(
            id=uuid.uuid4(),
            merchant_id=m_id,
            max_automated_amount_paise=1_000_000,
            max_discount_percentage=5.0,
            max_retry_attempts=2,
            min_incremental_value_paise=10_000,
            human_approval_threshold_paise=1_000_000,
            min_contact_interval_hours=24,
            enforce_opt_out=True,
            block_disputed=True,
            block_fraud_signals=True,
            is_active=True,
        )
        db.add(policy)
        await db.commit()

    return {
        "id": str(policy.id),
        "max_automated_amount_paise": policy.max_automated_amount_paise,
        "max_automated_amount_rupees": policy.max_automated_amount_paise / 100.0,
        "max_discount_percentage": policy.max_discount_percentage,
        "max_retry_attempts": policy.max_retry_attempts,
        "min_incremental_value_paise": policy.min_incremental_value_paise,
        "min_incremental_value_rupees": policy.min_incremental_value_paise / 100.0,
        "human_approval_threshold_paise": policy.human_approval_threshold_paise,
        "human_approval_threshold_rupees": policy.human_approval_threshold_paise / 100.0,
        "min_contact_interval_hours": policy.min_contact_interval_hours,
        "enforce_opt_out": policy.enforce_opt_out,
        "block_disputed": policy.block_disputed,
        "block_fraud_signals": policy.block_fraud_signals,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
    }


@router.put("")
async def update_policy(payload: PolicyUpdateSchema, db: AsyncSession = Depends(get_db)):
    """Update active policy settings with immutable audit trail record."""
    stmt = select(MerchantPolicy).where(MerchantPolicy.is_active == True)
    res = await db.execute(stmt)
    policy = res.scalars().first()

    if not policy:
        raise HTTPException(status_code=404, detail="No active policy found")

    old_config = {
        "max_automated_amount_paise": policy.max_automated_amount_paise,
        "max_discount_percentage": policy.max_discount_percentage,
        "max_retry_attempts": policy.max_retry_attempts,
        "min_incremental_value_paise": policy.min_incremental_value_paise,
        "human_approval_threshold_paise": policy.human_approval_threshold_paise,
    }

    update_dict = payload.model_dump(exclude_none=True)
    for k, v in update_dict.items():
        setattr(policy, k, v)
    policy.updated_at = datetime.now(timezone.utc)

    # Log policy update event
    await AuditEngine.log_event(
        db=db,
        merchant_id=policy.merchant_id,
        event_type=EventType.POLICY_UPDATED,
        actor="merchant_admin",
        entity_type="policy",
        entity_id=policy.id,
        reason="Merchant updated financial risk thresholds",
        metadata={"previous": old_config, "updates": update_dict},
    )

    await db.commit()
    return {"status": "updated", "updates": update_dict}
