"""
Recovery Engine — Master Orchestration Workflow.

Executes the complete core loop:
DETECT -> SIMULATE -> DECIDE -> CONTROL -> ACT -> MEASURE -> LEARN
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.customer import Customer
from models.payment import Payment
from models.recovery_opportunity import RecoveryOpportunity
from models.recovery_action import RecoveryAction
from models.policy import MerchantPolicy
from models.model_prediction import ModelPrediction
from events.event_types import (
    WorkflowState,
    ActionType,
    PolicyStatus,
    RiskStatus,
    EventType,
)
from domain.workflow import WorkflowStateMachine
from domain.policy_engine import (
    PolicyEngine,
    PolicyConfig,
    RecoveryContext,
    RecommendedAction,
)
from domain.decision_engine import DecisionEngine, ActionRanking
from domain.risk_firewall import RiskFirewall
from domain.audit_engine import AuditEngine
from ml.model_registry import ModelRegistry
from integrations.razorpay_client import RazorpayClientWrapper
from utils.logging import get_logger

logger = get_logger("recovery_engine")


class RecoveryEngine:
    """Orchestrates end-to-end recovery opportunities."""

    def __init__(self, rzp_client: Optional[RazorpayClientWrapper] = None):
        self.rzp_client = rzp_client or RazorpayClientWrapper()
        self.model_registry = ModelRegistry.get_instance()
        self.decision_engine = DecisionEngine()
        self.risk_firewall = RiskFirewall()

    async def process_payment_failure(
        self,
        db: AsyncSession,
        payment: Payment,
        customer: Customer,
        merchant_id: uuid.UUID,
    ) -> RecoveryOpportunity:
        """
        Ingest a failed payment and execute the decision pipeline.
        """
        # 1. DETECT: Create or fetch Recovery Opportunity
        opportunity = RecoveryOpportunity(
            id=uuid.uuid4(),
            payment_id=payment.id,
            customer_id=customer.id,
            amount_paise=payment.amount_paise,
            workflow_state=WorkflowState.DETECTED.value,
            retry_count=0,
            detected_at=datetime.now(timezone.utc),
        )
        db.add(opportunity)
        await db.flush()

        await AuditEngine.log_event(
            db=db,
            merchant_id=merchant_id,
            event_type=EventType.RECOVERY_DETECTED,
            workflow_id=opportunity.id,
            entity_type="recovery_opportunity",
            entity_id=opportunity.id,
            previous_state=None,
            new_state=WorkflowState.DETECTED,
            reason=f"Payment failure detected: {payment.failure_reason}",
            metadata={"amount_paise": payment.amount_paise, "method": payment.payment_method},
        )

        # 2. ANALYZE: Feature Extraction & Model Inference
        opportunity.workflow_state = WorkflowState.ANALYZING.value
        await db.flush()

        tx_dict = {
            "amount": payment.amount_paise / 100.0,
            "amount_paise": payment.amount_paise,
            "payment_method": payment.payment_method,
            "failure_reason": payment.failure_reason or "unknown",
            "hour_of_day": datetime.now(timezone.utc).hour,
            "day_of_week": datetime.now(timezone.utc).weekday(),
        }
        cust_dict = {
            "segment": customer.segment,
            "historical_orders": customer.historical_orders,
            "success_rate": 0.8 if customer.historical_orders == 0 else customer.successful_payments / max(customer.historical_orders, 1),
            "historical_recovery_rate": customer.historical_recovery_rate,
            "opted_out": customer.opted_out,
            "has_active_dispute": customer.has_active_dispute,
        }

        # Predict recovery probabilities across all actions
        probabilities = self.model_registry.predict_action_probabilities(
            transaction_dict=tx_dict,
            customer_dict=cust_dict,
            retry_count=opportunity.retry_count,
        )

        # Record model predictions for audit
        for act_type, prob in probabilities.items():
            pred_record = ModelPrediction(
                id=uuid.uuid4(),
                opportunity_id=opportunity.id,
                model_version="1.0.0",
                action_type=act_type.value,
                predicted_probability=prob,
                predicted_at=datetime.now(timezone.utc),
            )
            db.add(pred_record)

        # 3. DECIDE: Rank actions via economic value function
        ranking: ActionRanking = self.decision_engine.evaluate_actions(
            amount_paise=payment.amount_paise,
            predictions=probabilities,
            min_incremental_value_paise=10_000,  # Min INR 100 incremental value
        )

        opportunity.recommended_action = ranking.recommended_action.value if ranking.recommended_action else ActionType.DO_NOTHING.value
        opportunity.baseline_probability = probabilities.get(ActionType.DO_NOTHING, 0.3)
        opportunity.recommended_probability = probabilities.get(ranking.recommended_action, opportunity.baseline_probability)
        opportunity.expected_incremental_value_paise = ranking.recommended_incremental_value_paise
        opportunity.action_rankings = ranking.to_dict()
        opportunity.feature_vector = {**tx_dict, **cust_dict}
        opportunity.workflow_state = WorkflowState.RECOMMENDED.value
        await db.flush()

        await AuditEngine.log_event(
            db=db,
            merchant_id=merchant_id,
            event_type=EventType.RECOVERY_RECOMMENDED,
            workflow_id=opportunity.id,
            entity_type="recovery_opportunity",
            entity_id=opportunity.id,
            previous_state=WorkflowState.ANALYZING,
            new_state=WorkflowState.RECOMMENDED,
            reason=f"Recommended {opportunity.recommended_action} with incremental value INR {opportunity.expected_incremental_value_paise/100:.2f}",
            metadata=ranking.to_dict(),
        )

        # 4. CONTROL: Risk Firewall & Policy Engine
        opportunity.workflow_state = WorkflowState.POLICY_CHECK.value
        await db.flush()

        # Fetch active merchant policy
        pol_stmt = select(MerchantPolicy).where(
            MerchantPolicy.merchant_id == merchant_id,
            MerchantPolicy.is_active == True
        )
        pol_res = await db.execute(pol_stmt)
        policy_model = pol_res.scalars().first()

        policy_config = PolicyConfig(
            max_automated_amount_paise=policy_model.max_automated_amount_paise if policy_model else 1_000_000,
            max_discount_percentage=policy_model.max_discount_percentage if policy_model else 5.0,
            max_retry_attempts=policy_model.max_retry_attempts if policy_model else 2,
            min_incremental_value_paise=policy_model.min_incremental_value_paise if policy_model else 10_000,
            human_approval_threshold_paise=policy_model.human_approval_threshold_paise if policy_model else 1_000_000,
            enforce_opt_out=policy_model.enforce_opt_out if policy_model else True,
            block_disputed=policy_model.block_disputed if policy_model else True,
            block_fraud_signals=policy_model.block_fraud_signals if policy_model else True,
        )

        rec_act_obj = RecommendedAction(
            action_type=ActionType(opportunity.recommended_action),
            expected_incremental_value_paise=opportunity.expected_incremental_value_paise or 0,
            discount_percentage=5.0 if opportunity.recommended_action == ActionType.DISCOUNT.value else 0.0,
        )
        rec_context = RecoveryContext(
            amount_paise=payment.amount_paise,
            customer_opted_out=customer.opted_out,
            customer_has_dispute=customer.has_active_dispute,
            retry_count=opportunity.retry_count,
        )

        pol_engine = PolicyEngine(policy_config)
        policy_eval = pol_engine.evaluate(rec_act_obj, rec_context)

        opportunity.policy_result = policy_eval.status.value
        opportunity.policy_checks = policy_eval.to_dict()
        await db.flush()

        # 5. ROUTE BASED ON POLICY RESULT
        if policy_eval.is_blocked:
            opportunity.workflow_state = WorkflowState.BLOCKED.value
            await db.flush()
            await AuditEngine.log_event(
                db=db,
                merchant_id=merchant_id,
                event_type=EventType.RECOVERY_BLOCKED,
                workflow_id=opportunity.id,
                new_state=WorkflowState.BLOCKED,
                reason=f"Policy blocked action: {', '.join(policy_eval.blocking_rules)}",
                metadata=policy_eval.to_dict(),
            )
            return opportunity

        elif policy_eval.requires_human:
            opportunity.workflow_state = WorkflowState.PENDING_APPROVAL.value
            
            # Create a pending RecoveryAction and Approval record
            action_record = RecoveryAction(
                id=uuid.uuid4(),
                opportunity_id=opportunity.id,
                action_type=opportunity.recommended_action,
                status="pending_approval",
                idempotency_key=f"act_{uuid.uuid4().hex}",
                action_cost_paise=DEFAULT_ACTION_COSTS.get(ActionType(opportunity.recommended_action), 0),
                discount_percentage=5.0 if opportunity.recommended_action == ActionType.DISCOUNT.value else 0.0,
                created_at=datetime.now(timezone.utc),
            )
            db.add(action_record)
            await db.flush()

            await AuditEngine.log_event(
                db=db,
                merchant_id=merchant_id,
                event_type=EventType.RECOVERY_APPROVAL_REQUESTED,
                workflow_id=opportunity.id,
                new_state=WorkflowState.PENDING_APPROVAL,
                reason="High-value transaction requires human approval",
                metadata={"action_id": str(action_record.id)},
            )
            return opportunity

        else:
            # Policy APPROVED -> Transition to APPROVED and EXECUTE
            opportunity.workflow_state = WorkflowState.APPROVED.value
            await db.flush()

            await self.execute_approved_action(
                db=db,
                opportunity=opportunity,
                payment=payment,
                customer=customer,
                merchant_id=merchant_id,
            )
            return opportunity

    async def execute_approved_action(
        self,
        db: AsyncSession,
        opportunity: RecoveryOpportunity,
        payment: Payment,
        customer: Customer,
        merchant_id: uuid.UUID,
    ) -> RecoveryAction:
        """
        Execute an approved action (e.g. create Razorpay payment link or dispatch simulated recovery).
        """
        opportunity.workflow_state = WorkflowState.EXECUTING.value
        await db.flush()

        action_type_str = opportunity.recommended_action or ActionType.DO_NOTHING.value
        act_enum = ActionType(action_type_str)

        # Create action record
        action_record = RecoveryAction(
            id=uuid.uuid4(),
            opportunity_id=opportunity.id,
            action_type=action_type_str,
            status="executing",
            idempotency_key=f"act_{uuid.uuid4().hex}",
            action_cost_paise=1000 if act_enum == ActionType.RETRY else 2000 if act_enum in (ActionType.PAYMENT_LINK, ActionType.DISCOUNT) else 500 if act_enum == ActionType.REMINDER else 0,
            discount_percentage=5.0 if act_enum == ActionType.DISCOUNT else 0.0,
            discount_amount_paise=int(payment.amount_paise * 0.05) if act_enum == ActionType.DISCOUNT else 0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(action_record)
        await db.flush()

        # Execute via Razorpay integration if applicable
        if act_enum in (ActionType.PAYMENT_LINK, ActionType.DISCOUNT):
            effective_amount = payment.amount_paise
            if act_enum == ActionType.DISCOUNT:
                effective_amount = int(payment.amount_paise * 0.95)

            plink_res = self.rzp_client.create_payment_link(
                amount_paise=effective_amount,
                customer_name=f"Customer {customer.external_id[:8]}",
                customer_email=f"{customer.external_id[:8]}@example.com",
                description=f"Recovery for Order {payment.order_id}",
                reference_id=f"rec_{opportunity.id.hex[:12]}",
            )
            action_record.razorpay_payment_link_id = plink_res.get("id")
            action_record.execution_metadata = plink_res

        action_record.status = "executed"
        action_record.executed_at = datetime.now(timezone.utc)
        opportunity.workflow_state = WorkflowState.WAITING_OUTCOME.value
        await db.flush()

        await AuditEngine.log_event(
            db=db,
            merchant_id=merchant_id,
            event_type=EventType.RECOVERY_EXECUTED,
            workflow_id=opportunity.id,
            entity_type="recovery_action",
            entity_id=action_record.id,
            previous_state=WorkflowState.EXECUTING,
            new_state=WorkflowState.WAITING_OUTCOME,
            reason=f"Action {action_type_str} successfully dispatched",
            metadata={"action_id": str(action_record.id), "idempotency_key": action_record.idempotency_key},
        )

        return action_record
