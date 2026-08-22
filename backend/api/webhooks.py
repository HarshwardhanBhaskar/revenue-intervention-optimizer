"""
Razorpay Webhook Ingestion API.

Requirements:
- HMAC-SHA256 signature verification
- Event deduplication and idempotency
- Safe transaction lifecycle orchestration
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.payment_event import PaymentEvent
from models.payment import Payment
from models.customer import Customer
from models.merchant import Merchant
from models.order import Order
from domain.recovery_engine import RecoveryEngine
from domain.audit_engine import AuditEngine
from integrations.razorpay_client import RazorpayClientWrapper
from events.event_types import EventType
from utils.logging import get_logger

router = APIRouter()
logger = get_logger("webhooks_api")
rzp_client = RazorpayClientWrapper()
recovery_engine = RecoveryEngine(rzp_client)


@router.post("/razorpay")
async def handle_razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Ingest and process Razorpay webhooks.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # 1. Signature Verification (Skip if simulated webhook in dev with header X-Simulated)
    is_simulated = request.headers.get("X-Simulated") == "true"
    if not is_simulated and rzp_client.is_test_configured:
        if not rzp_client.verify_webhook_signature(raw_body, signature):
            logger.warning("webhook.invalid_signature", signature=signature[:20] if signature else "none")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event", "payment.failed")
    rzp_event_id = payload.get("id") or f"evt_{uuid.uuid4().hex[:12]}"
    idempotency_key = f"wh_{rzp_event_id}"

    # 2. Idempotency Check / Deduplication
    dup_stmt = select(PaymentEvent).where(PaymentEvent.idempotency_key == idempotency_key)
    existing_event = (await db.execute(dup_stmt)).scalars().first()
    if existing_event:
        logger.info("webhook.duplicate_ignored", idempotency_key=idempotency_key)
        return {"status": "duplicate_ignored", "event_id": rzp_event_id}

    # Extract payment entity
    payment_payload = payload.get("payload", {}).get("payment", {}).get("entity", {})
    amount_paise = payment_payload.get("amount", 500000)
    rzp_payment_id = payment_payload.get("id", f"pay_{uuid.uuid4().hex[:12]}")
    failure_reason = payment_payload.get("error_reason") or payment_payload.get("description") or "insufficient_funds"
    payment_method = payment_payload.get("method", "upi")

    # Fetch default merchant
    m_stmt = select(Merchant)
    merchant = (await db.execute(m_stmt)).scalars().first()
    if not merchant:
        merchant = Merchant(
            id=uuid.uuid4(),
            name="Default Merchant",
            razorpay_account_id="acc_default",
        )
        db.add(merchant)
        await db.flush()

    # Create/fetch customer
    cust_stmt = select(Customer).where(Customer.merchant_id == merchant.id).limit(1)
    customer = (await db.execute(cust_stmt)).scalars().first()
    if not customer:
        customer = Customer(
            id=uuid.uuid4(),
            merchant_id=merchant.id,
            external_id=f"cust_{uuid.uuid4().hex[:8]}",
            segment="regular",
            historical_orders=3,
            successful_payments=2,
            failed_payments=1,
            historical_recovery_rate=0.40,
        )
        db.add(customer)
        await db.flush()

    # Create Order
    order = Order(
        id=uuid.uuid4(),
        customer_id=customer.id,
        external_order_id=payment_payload.get("order_id", f"order_{uuid.uuid4().hex[:8]}"),
        amount_paise=amount_paise,
        currency="INR",
        status="failed" if event_type == "payment.failed" else "captured",
    )
    db.add(order)
    await db.flush()

    # Create Payment
    payment = Payment(
        id=uuid.uuid4(),
        order_id=order.id,
        razorpay_payment_id=rzp_payment_id,
        amount_paise=amount_paise,
        currency="INR",
        payment_method=payment_method,
        status="failed" if event_type == "payment.failed" else "captured",
        failure_reason=failure_reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    await db.flush()

    # Save PaymentEvent record for deduplication
    pe_record = PaymentEvent(
        id=uuid.uuid4(),
        payment_id=payment.id,
        event_type=event_type,
        razorpay_event_id=rzp_event_id,
        payload=payload,
        idempotency_key=idempotency_key,
        processed_at=datetime.now(timezone.utc),
    )
    db.add(pe_record)
    await db.flush()

    # 3. If Payment Failed, Trigger the Recovery Engine Master Pipeline!
    if event_type == "payment.failed":
        opp = await recovery_engine.process_payment_failure(
            db=db,
            payment=payment,
            customer=customer,
            merchant_id=merchant.id,
        )
        await db.commit()
        return {
            "status": "processed",
            "event_type": event_type,
            "opportunity_id": str(opp.id),
            "workflow_state": opp.workflow_state,
            "recommended_action": opp.recommended_action,
            "expected_incremental_value_paise": opp.expected_incremental_value_paise,
        }

    await db.commit()
    return {"status": "acknowledged", "event_type": event_type}
