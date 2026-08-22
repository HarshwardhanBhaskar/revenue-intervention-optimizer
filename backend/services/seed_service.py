"""
Database Seeder Service.

Populates PostgreSQL with rich, realistic merchant data, customer profiles,
historical recovery opportunities, outcomes, audit events, and active policies.
"""

import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.merchant import Merchant
from models.customer import Customer
from models.order import Order
from models.payment import Payment
from models.policy import MerchantPolicy
from models.recovery_opportunity import RecoveryOpportunity
from models.recovery_action import RecoveryAction
from models.recovery_outcome import RecoveryOutcome
from models.audit_event import AuditEvent
from models.experiment import Experiment
from models.experiment_assignment import ExperimentAssignment
from events.event_types import WorkflowState, ActionType, EventType
from utils.logging import get_logger

logger = get_logger("seeder")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class SeedService:
    @staticmethod
    async def seed_database(db: AsyncSession):
        logger.info("seeder.starting_seed")

        # 1. Check if already seeded
        res = await db.execute(select(Merchant))
        existing_merchant = res.scalars().first()
        if existing_merchant:
            logger.info("seeder.already_seeded", merchant_id=str(existing_merchant.id))
            return existing_merchant

        # 2. Create Default Merchant
        merchant = Merchant(
            id=uuid.uuid4(),
            name="Apex Direct D2C India",
            razorpay_account_id="acc_test_apex_d2c",
            settings={"currency": "INR", "tier": "growth"},
            created_at=datetime.now(timezone.utc) - timedelta(days=180),
        )
        db.add(merchant)
        await db.flush()

        # 3. Create Default Active Policy
        policy = MerchantPolicy(
            id=uuid.uuid4(),
            merchant_id=merchant.id,
            max_automated_amount_paise=1_000_000,  # INR 10,000 auto-approval cap
            max_discount_percentage=5.0,
            max_retry_attempts=2,
            min_incremental_value_paise=10_000,    # Min INR 100 net gain
            human_approval_threshold_paise=1_000_000,
            min_contact_interval_hours=24,
            enforce_opt_out=True,
            block_disputed=True,
            block_fraud_signals=True,
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=180),
        )
        db.add(policy)
        await db.flush()

        # 4. Load Customers
        cust_file = DATA_DIR / "raw" / "customers.csv"
        cust_map = {}
        if cust_file.exists():
            cust_df = pd.read_csv(cust_file)
            for _, row in cust_df.iterrows():
                cid = uuid.UUID(row["customer_id"]) if len(str(row["customer_id"])) == 36 else uuid.uuid4()
                customer = Customer(
                    id=cid,
                    merchant_id=merchant.id,
                    external_id=f"cust_{str(cid)[:8]}",
                    segment=row["segment"],
                    historical_orders=int(row["historical_orders"]),
                    successful_payments=int(row["successful_payments"]),
                    failed_payments=int(row["failed_payments"]),
                    historical_recovery_rate=float(row["historical_recovery_rate"]),
                    communication_preference=str(row["communication_preference"]),
                    opted_out=bool(row["opted_out"]),
                    has_active_dispute=bool(row["has_active_dispute"]),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random_int(30, 200)),
                )
                db.add(customer)
                cust_map[str(row["customer_id"])] = customer
            await db.flush()

        # 5. Load Transactions & Seed Opportunities
        train_tx_file = DATA_DIR / "splits" / "train" / "transactions.csv"
        train_obs_file = DATA_DIR / "splits" / "train" / "observed.csv"
        
        if train_tx_file.exists() and train_obs_file.exists():
            tx_df = pd.read_csv(train_tx_file).head(300)  # Seed 300 rich records for fast boot
            obs_df = pd.read_csv(train_obs_file).set_index("transaction_id")

            for _, row in tx_df.iterrows():
                tx_id_str = str(row["transaction_id"])
                cust_obj = cust_map.get(str(row["customer_id"]))
                if not cust_obj:
                    continue

                # Create Order
                order = Order(
                    id=uuid.uuid4(),
                    customer_id=cust_obj.id,
                    external_order_id=str(row["order_id"]),
                    amount_paise=int(row["amount_paise"]),
                    currency="INR",
                    status="completed" if obs_df.loc[tx_id_str, "payment_success"] else "failed",
                    created_at=pd.to_datetime(row["timestamp"]).to_pydatetime().replace(tzinfo=timezone.utc),
                )
                db.add(order)
                await db.flush()

                # Create Payment
                payment = Payment(
                    id=uuid.uuid4(),
                    order_id=order.id,
                    razorpay_payment_id=f"pay_{uuid.uuid4().hex[:14]}",
                    amount_paise=int(row["amount_paise"]),
                    currency="INR",
                    payment_method=str(row["payment_method"]),
                    status="captured" if obs_df.loc[tx_id_str, "payment_success"] else "failed",
                    failure_reason=str(row["failure_reason"]),
                    created_at=order.created_at,
                )
                db.add(payment)
                await db.flush()

                # Create Opportunity
                obs = obs_df.loc[tx_id_str]
                is_success = bool(obs["payment_success"])
                action_taken = str(obs["action_taken"])
                
                opp = RecoveryOpportunity(
                    id=uuid.uuid4(),
                    payment_id=payment.id,
                    customer_id=cust_obj.id,
                    amount_paise=payment.amount_paise,
                    workflow_state=WorkflowState.RECOVERED.value if is_success else WorkflowState.FAILED.value,
                    recommended_action=action_taken,
                    baseline_probability=0.35,
                    recommended_probability=float(obs["recovery_probability"]),
                    expected_incremental_value_paise=int((float(obs["recovery_probability"]) - 0.35) * payment.amount_paise),
                    confidence=0.88,
                    retry_count=1 if action_taken == "retry" else 0,
                    policy_result="approved",
                    risk_result="clear",
                    detected_at=payment.created_at,
                    resolved_at=payment.created_at + timedelta(minutes=15),
                )
                db.add(opp)
                await db.flush()

                # Action Record
                act_rec = RecoveryAction(
                    id=uuid.uuid4(),
                    opportunity_id=opp.id,
                    action_type=action_taken,
                    status="executed",
                    idempotency_key=f"act_{uuid.uuid4().hex}",
                    action_cost_paise=int(obs["action_cost"] * 100),
                    discount_percentage=float(obs["discount_percentage"]),
                    discount_amount_paise=int(obs["discount_amount"] * 100),
                    created_at=payment.created_at,
                    executed_at=payment.created_at + timedelta(seconds=10),
                )
                db.add(act_rec)
                await db.flush()

                # Outcome Record
                out_rec = RecoveryOutcome(
                    id=uuid.uuid4(),
                    action_id=act_rec.id,
                    opportunity_id=opp.id,
                    payment_success=is_success,
                    recovered_amount_paise=payment.amount_paise if is_success else 0,
                    observed_at=payment.created_at + timedelta(minutes=15),
                )
                db.add(out_rec)

                # Audit event
                audit = AuditEvent(
                    id=uuid.uuid4(),
                    merchant_id=merchant.id,
                    workflow_id=opp.id,
                    event_type=EventType.RECOVERY_COMPLETED.value if is_success else EventType.RECOVERY_FAILED.value,
                    actor="ai_engine",
                    entity_type="recovery_opportunity",
                    entity_id=opp.id,
                    new_state=opp.workflow_state,
                    reason=f"Action {action_taken} produced outcome {'RECOVERED' if is_success else 'FAILED'}",
                    metadata_json={"amount_paise": payment.amount_paise, "action": action_taken},
                    created_at=payment.created_at + timedelta(minutes=15),
                )
                db.add(audit)

        # 6. Add 3 High-Value PENDING_APPROVAL Opportunities for Demo
        pending_samples = [
            {"amt": 28500_00, "seg": "premium", "method": "credit_card", "reason": "authentication_failed", "rec": "payment_link", "inc": 14200_00},
            {"amt": 18999_00, "seg": "loyal", "method": "upi", "reason": "timeout", "rec": "payment_link", "inc": 8500_00},
            {"amt": 12500_00, "seg": "price_sensitive", "method": "debit_card", "reason": "insufficient_funds", "rec": "discount", "inc": 4200_00},
        ]

        for p_data in pending_samples:
            p_cust = Customer(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                external_id=f"vip_{uuid.uuid4().hex[:6]}",
                segment=p_data["seg"],
                historical_orders=15,
                successful_payments=14,
                failed_payments=1,
                historical_recovery_rate=0.75,
                created_at=datetime.now(timezone.utc) - timedelta(days=60),
            )
            db.add(p_cust)
            await db.flush()

            p_order = Order(
                id=uuid.uuid4(),
                customer_id=p_cust.id,
                external_order_id=f"order_{uuid.uuid4().hex[:8]}",
                amount_paise=p_data["amt"],
                currency="INR",
                status="pending",
                created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            )
            db.add(p_order)
            await db.flush()

            p_payment = Payment(
                id=uuid.uuid4(),
                order_id=p_order.id,
                razorpay_payment_id=f"pay_{uuid.uuid4().hex[:12]}",
                amount_paise=p_data["amt"],
                currency="INR",
                payment_method=p_data["method"],
                status="failed",
                failure_reason=p_data["reason"],
                created_at=p_order.created_at,
            )
            db.add(p_payment)
            await db.flush()

            p_opp = RecoveryOpportunity(
                id=uuid.uuid4(),
                payment_id=p_payment.id,
                customer_id=p_cust.id,
                amount_paise=p_data["amt"],
                workflow_state=WorkflowState.PENDING_APPROVAL.value,
                recommended_action=p_data["rec"],
                baseline_probability=0.28,
                recommended_probability=0.74,
                expected_incremental_value_paise=p_data["inc"],
                confidence=0.91,
                policy_result="requires_human",
                risk_result="clear",
                policy_checks={
                    "status": "requires_human",
                    "checks": [
                        {"rule": "human_approval_threshold", "passed": True, "details": f"Amount INR {p_data['amt']/100:,.0f} exceeds auto threshold INR 10,000"}
                    ]
                },
                detected_at=p_order.created_at,
            )
            db.add(p_opp)
            await db.flush()

            p_act = RecoveryAction(
                id=uuid.uuid4(),
                opportunity_id=p_opp.id,
                action_type=p_data["rec"],
                status="pending_approval",
                idempotency_key=f"act_{uuid.uuid4().hex}",
                action_cost_paise=2000,
                discount_percentage=5.0 if p_data["rec"] == "discount" else 0.0,
                created_at=p_order.created_at,
            )
            db.add(p_act)

        # 7. Seed Active Experiment
        exp = Experiment(
            id=uuid.uuid4(),
            merchant_id=merchant.id,
            name="AI Intervention Optimizer vs Baseline Retry",
            status="active",
            control_pct=0.5,
            treatment_pct=0.5,
            config={"control_policy": "retry_once", "treatment_policy": "t_learner_uplift"},
            results={"incremental_net_uplift_pct": 15.7, "sample_size": 538},
            started_at=datetime.now(timezone.utc) - timedelta(days=30),
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(exp)
        await db.commit()

        logger.info("seeder.completed_successfully", merchant_id=str(merchant.id))
        return merchant


def random_int(a: int, b: int) -> int:
    import random
    return random.randint(a, b)
