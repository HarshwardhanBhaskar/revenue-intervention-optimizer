"""Dashboard API — Live financial operations metrics and recovery pipeline."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.database import get_db
from models.recovery_opportunity import RecoveryOpportunity
from models.recovery_action import RecoveryAction
from models.recovery_outcome import RecoveryOutcome
from models.payment import Payment

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Aggregate live metrics for the merchant."""
    # Total opportunities count
    opp_count_stmt = select(func.count(RecoveryOpportunity.id))
    total_opportunities = (await db.execute(opp_count_stmt)).scalar() or 0

    # Total revenue at risk
    risk_stmt = select(func.sum(RecoveryOpportunity.amount_paise))
    revenue_at_risk_paise = (await db.execute(risk_stmt)).scalar() or 0

    # Total gross recovered
    rec_stmt = select(func.sum(RecoveryOutcome.recovered_amount_paise)).where(
        RecoveryOutcome.payment_success == True
    )
    recovered_paise = (await db.execute(rec_stmt)).scalar() or 0

    # Total intervention and discount costs
    cost_stmt = select(
        func.sum(RecoveryAction.action_cost_paise),
        func.sum(RecoveryAction.discount_amount_paise),
    )
    cost_res = (await db.execute(cost_stmt)).first()
    action_cost_paise = cost_res[0] or 0
    discount_cost_paise = cost_res[1] or 0
    total_cost_paise = action_cost_paise + discount_cost_paise

    # Recovered count
    rec_count_stmt = select(func.count(RecoveryOutcome.id)).where(
        RecoveryOutcome.payment_success == True
    )
    recovered_count = (await db.execute(rec_count_stmt)).scalar() or 0

    # Recovery rate
    recovery_rate = recovered_count / max(total_opportunities, 1)

    # Actions executed breakdown
    do_nothing_stmt = select(func.count(RecoveryOpportunity.id)).where(
        RecoveryOpportunity.recommended_action == "do_nothing"
    )
    do_nothing_count = (await db.execute(do_nothing_stmt)).scalar() or 0
    interventions_executed = max(0, total_opportunities - do_nothing_count)

    # Incremental net calculations (vs estimated 35% baseline without optimization)
    baseline_recovery_rate = 0.35
    baseline_recovered_paise = int(revenue_at_risk_paise * baseline_recovery_rate)
    incremental_recovered_paise = max(0, recovered_paise - baseline_recovered_paise)
    net_incremental_value_paise = max(0, incremental_recovered_paise - total_cost_paise)
    improvement_pct = ((recovery_rate - baseline_recovery_rate) / baseline_recovery_rate) * 100 if baseline_recovery_rate > 0 else 0

    return {
        "revenue_at_risk_paise": revenue_at_risk_paise,
        "recovered_paise": recovered_paise,
        "incremental_recovered_paise": incremental_recovered_paise,
        "recovery_rate": round(recovery_rate, 4),
        "baseline_recovery_rate": round(baseline_recovery_rate, 4),
        "improvement_vs_baseline": round(improvement_pct, 1),
        "total_opportunities": total_opportunities,
        "interventions_executed": interventions_executed,
        "do_nothing_count": do_nothing_count,
        "net_incremental_value_paise": net_incremental_value_paise,
        "total_intervention_cost_paise": total_cost_paise,
        "action_cost_paise": action_cost_paise,
        "discount_cost_paise": discount_cost_paise,
    }


@router.get("/trends")
async def get_dashboard_trends(db: AsyncSession = Depends(get_db)):
    """Get time-series data for recovery trend chart."""
    # Grouped sample trend data representing monthly progression
    return {
        "trends": [
            {"month": "Jan", "at_risk": 4200000, "recovered": 2100000, "baseline": 1470000, "incremental": 630000},
            {"month": "Feb", "at_risk": 4800000, "recovered": 2550000, "baseline": 1680000, "incremental": 870000},
            {"month": "Mar", "at_risk": 5100000, "recovered": 2850000, "baseline": 1785000, "incremental": 1065000},
            {"month": "Apr", "at_risk": 4900000, "recovered": 2900000, "baseline": 1715000, "incremental": 1185000},
            {"month": "May", "at_risk": 5300000, "recovered": 3200000, "baseline": 1855000, "incremental": 1345000},
            {"month": "Jun", "at_risk": 5600000, "recovered": 3450000, "baseline": 1960000, "incremental": 1490000},
            {"month": "Jul", "at_risk": 5800000, "recovered": 3600000, "baseline": 2030000, "incremental": 1570000},
        ]
    }


@router.get("/pipeline")
async def get_recovery_pipeline(db: AsyncSession = Depends(get_db)):
    """Recovery pipeline funnel stages."""
    total_stmt = select(func.count(RecoveryOpportunity.id))
    total = (await db.execute(total_stmt)).scalar() or 0

    pending_stmt = select(func.count(RecoveryOpportunity.id)).where(
        RecoveryOpportunity.workflow_state == "pending_approval"
    )
    pending = (await db.execute(pending_stmt)).scalar() or 0

    acting_stmt = select(func.count(RecoveryOpportunity.id)).where(
        RecoveryOpportunity.workflow_state.in_(["executing", "waiting_outcome"])
    )
    acting = (await db.execute(acting_stmt)).scalar() or 0

    recovered_stmt = select(func.count(RecoveryOpportunity.id)).where(
        RecoveryOpportunity.workflow_state == "recovered"
    )
    recovered = (await db.execute(recovered_stmt)).scalar() or 0

    do_nothing_stmt = select(func.count(RecoveryOpportunity.id)).where(
        RecoveryOpportunity.recommended_action == "do_nothing"
    )
    do_nothing = (await db.execute(do_nothing_stmt)).scalar() or 0

    return {
        "pipeline": [
            {"stage": "Detected Risk", "count": total, "color": "var(--color-text-secondary)"},
            {"stage": "AI Analyzed & Ranked", "count": total, "color": "var(--color-info)"},
            {"stage": "Pending Approval", "count": pending, "color": "var(--color-warning)"},
            {"stage": "Interventions Dispatched", "count": max(0, total - do_nothing - pending), "color": "var(--color-info)"},
            {"stage": "Successfully Recovered", "count": recovered, "color": "var(--color-positive)"},
            {"stage": "Optimized DO_NOTHING", "count": do_nothing, "color": "var(--color-text-muted)"},
        ]
    }
