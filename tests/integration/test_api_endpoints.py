"""
Integration Tests for REST APIs and End-to-End Recovery Flow.

Tests:
1. Dashboard summary and trends
2. Opportunities list and counterfactual Decision Lab simulation
3. Approval Queue, Action Approve and Reject (with audit events)
4. Policy read and update
5. Webhook ingestion and idempotency deduplication
6. AI Assistant grounded Q&A
"""

import pytest
import pytest_asyncio
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from main import create_app
from models.database import init_db, get_async_session_factory
from services.seed_service import SeedService


@pytest_asyncio.fixture(scope="module")
async def app_client():
    await init_db()
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        await SeedService.seed_database(session)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(app_client: AsyncClient):
    res = await app_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_dashboard_summary(app_client: AsyncClient):
    res = await app_client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "revenue_at_risk_paise" in data
    assert "incremental_recovered_paise" in data
    assert "recovery_rate" in data
    assert data["total_opportunities"] > 0


@pytest.mark.asyncio
async def test_dashboard_trends_and_pipeline(app_client: AsyncClient):
    res_t = await app_client.get("/api/dashboard/trends")
    assert res_t.status_code == 200
    assert len(res_t.json()["trends"]) > 0

    res_p = await app_client.get("/api/dashboard/pipeline")
    assert res_p.status_code == 200
    assert len(res_p.json()["pipeline"]) >= 5


@pytest.mark.asyncio
async def test_opportunities_list_and_details(app_client: AsyncClient):
    res = await app_client.get("/api/opportunities")
    assert res.status_code == 200
    opps = res.json()["opportunities"]
    assert len(opps) > 0

    first_id = opps[0]["id"]
    res_detail = await app_client.get(f"/api/opportunities/{first_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == first_id


@pytest.mark.asyncio
async def test_decision_lab_simulation(app_client: AsyncClient):
    res = await app_client.get("/api/opportunities")
    first_id = res.json()["opportunities"][0]["id"]

    res_sim = await app_client.post(f"/api/opportunities/{first_id}/simulate")
    assert res_sim.status_code == 200
    data = res_sim.json()
    assert "action_comparisons" in data
    assert len(data["action_comparisons"]) == 5
    assert "discount_sensitivity" in data
    assert len(data["discount_sensitivity"]) == 4


@pytest.mark.asyncio
async def test_pending_approvals_and_action_flow(app_client: AsyncClient):
    import uuid
    from datetime import datetime, timezone
    from models.recovery_opportunity import RecoveryOpportunity
    from models.customer import Customer
    from models.payment import Payment
    from models.order import Order
    from models.merchant import Merchant
    from models.database import get_async_session_factory
    from sqlalchemy import select

    session_factory = get_async_session_factory()
    async with session_factory() as session:
        m = (await session.execute(select(Merchant))).scalars().first()
        c = (await session.execute(select(Customer))).scalars().first()
        p = (await session.execute(select(Payment))).scalars().first()

        # Create fresh pending opportunity
        test_opp = RecoveryOpportunity(
            id=uuid.uuid4(),
            payment_id=p.id,
            customer_id=c.id,
            amount_paise=2500000,
            workflow_state="pending_approval",
            recommended_action="payment_link",
            baseline_probability=0.25,
            recommended_probability=0.75,
            expected_incremental_value_paise=1200000,
            confidence=0.92,
            policy_result="requires_human",
            risk_result="clear",
            detected_at=datetime.now(timezone.utc),
        )
        session.add(test_opp)
        await session.commit()
        target_opp_id = str(test_opp.id)

    res_p = await app_client.get("/api/actions/pending")
    assert res_p.status_code == 200
    pending = res_p.json()["pending_actions"]
    assert len(pending) > 0

    # Approve action
    res_app = await app_client.post(f"/api/actions/{target_opp_id}/approve")
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "approved"

    # Verifying it cannot be re-approved (idempotent state guard)
    res_reapp = await app_client.post(f"/api/actions/{target_opp_id}/approve")
    assert res_reapp.status_code == 409


@pytest.mark.asyncio
async def test_policies_api(app_client: AsyncClient):
    res_get = await app_client.get("/api/policies")
    assert res_get.status_code == 200
    pol = res_get.json()
    assert "max_discount_percentage" in pol
    assert 0.0 <= pol["max_discount_percentage"] <= 25.0

    # Update policy
    target_val = 4.8
    res_put = await app_client.put(
        "/api/policies",
        json={"max_discount_percentage": target_val, "min_incremental_value_paise": 15000},
    )
    assert res_put.status_code == 200
    assert res_put.json()["updates"]["max_discount_percentage"] == target_val


@pytest.mark.asyncio
async def test_audit_events_stream(app_client: AsyncClient):
    res = await app_client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert len(data["events"]) > 0


@pytest.mark.asyncio
async def test_experiments_api(app_client: AsyncClient):
    res = await app_client.get("/api/experiments")
    assert res.status_code == 200
    data = res.json()
    assert len(data["experiments"]) > 0
    assert data["test_benchmark"] is not None


@pytest.mark.asyncio
async def test_ai_assistant_query(app_client: AsyncClient):
    res = await app_client.post(
        "/api/assistant/query",
        json={"query": "Why did the system choose DO NOTHING?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is True
    assert "DO_NOTHING" in data["response"]
    assert len(data["evidence"]) > 0


@pytest.mark.asyncio
async def test_webhook_ingestion_and_deduplication(app_client: AsyncClient):
    import uuid
    unique_evt_id = f"evt_test_{uuid.uuid4().hex[:8]}"
    webhook_payload = {
        "id": unique_evt_id,
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{uuid.uuid4().hex[:8]}",
                    "amount": 749900,
                    "method": "upi",
                    "error_reason": "network_error",
                }
            }
        },
    }

    # First delivery
    res1 = await app_client.post(
        "/api/webhooks/razorpay",
        json=webhook_payload,
        headers={"X-Simulated": "true"},
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"
    assert "opportunity_id" in res1.json()

    # Second delivery (Duplicate event)
    res2 = await app_client.post(
        "/api/webhooks/razorpay",
        json=webhook_payload,
        headers={"X-Simulated": "true"},
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate_ignored"
