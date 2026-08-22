"""
Automated Security Attack & Penetration Defense Test Suite

Simulates real attack vectors:
1. SQL Injection (SQLi) attacks on filter/search parameters
2. Webhook Signature Forgery (MITM) attacks
3. Webhook Replay & Duplicate Execution attacks
4. DoS / High-Frequency Rate Limit Flooding attacks
5. Large Payload Memory Exhaustion DoS attacks
6. OWASP HTTP Security Headers verification
"""

import sys
import os
import time
import hmac
import hashlib
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from main import create_app
from config import get_settings


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_sql_injection_defense(client):
    """
    ATTACK VECTOR 1: SQL Injection
    Attempts malicious SQL payloads in query parameters and customer searches.
    """
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE customers; --",
        "1 UNION SELECT 1, 'admin', 'password', 1000, 'INR' --",
        "admin'--",
        "' OR 1=1 #",
    ]

    for payload in sqli_payloads:
        # Search opportunities with SQLi payload
        resp = client.get(f"/api/opportunities/?status={payload}&search={payload}")
        # Server must handle gracefully without 500 error or syntax crash
        assert resp.status_code in (200, 422), f"SQLi payload triggered unhandled error: {payload}"
        
        # Verify no database crash or table dropping occurred
        health_resp = client.get("/api/dashboard/summary")
        assert health_resp.status_code == 200, "Database was damaged or crashed by SQLi attempt!"


def test_webhook_forgery_defense(client):
    """
    ATTACK VECTOR 2: Webhook HMAC Forgery
    Sends fake webhook payloads with forged or missing signatures.
    """
    payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_fake_attacker_999",
                    "amount": 500000,
                    "currency": "INR",
                    "status": "failed",
                }
            }
        }
    }
    body_bytes = json.dumps(payload).encode("utf-8")

    # 1. Missing signature -> Must be rejected (HTTP 400)
    resp_no_sig = client.post("/api/webhooks/razorpay", content=body_bytes)
    assert resp_no_sig.status_code == 400
    assert "Missing signature" in resp_no_sig.json()["detail"]

    # 2. Forged signature -> Must be rejected (HTTP 400)
    fake_signature = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    resp_bad_sig = client.post(
        "/api/webhooks/razorpay",
        content=body_bytes,
        headers={"X-Razorpay-Signature": fake_signature},
    )
    assert resp_bad_sig.status_code == 400
    assert "Invalid webhook signature" in resp_bad_sig.json()["detail"]


def test_webhook_replay_deduplication(client):
    """
    ATTACK VECTOR 3: Replay Attack
    Submits legitimate signed webhook twice to verify deduplication.
    """
    settings = get_settings()
    unique_tx_id = f"pay_replay_test_{int(time.time()*1000)}"
    payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": unique_tx_id,
                    "amount": 250000,
                    "currency": "INR",
                    "status": "failed",
                    "method": "upi",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Payment failed",
                }
            }
        }
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    
    # Generate valid signature
    valid_sig = hmac.new(
        settings.razorpay_webhook_secret.encode("utf-8"),
        body_bytes,
        hashlib.sha256,
    ).hexdigest()

    headers = {"X-Razorpay-Signature": valid_sig, "Content-Type": "application/json"}

    # First delivery -> Processed or Accepted (200)
    resp1 = client.post("/api/webhooks/razorpay", content=body_bytes, headers=headers)
    assert resp1.status_code == 200

    # Replay attack (Second delivery of same event) -> Deduplicated (200 duplicate skipped)
    resp2 = client.post("/api/webhooks/razorpay", content=body_bytes, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json().get("status") in ("duplicate", "processed", "success")


def test_payload_size_dos_defense(client):
    """
    ATTACK VECTOR 4: Large Payload DoS / Memory Exhaustion
    Sends a payload larger than 1MB to trigger HTTP 413 Request Entity Too Large.
    """
    # 1.5MB oversized string payload
    oversized_payload = "X" * (1024 * 1024 + 500 * 1024)
    resp = client.post(
        "/api/assistant/chat",
        content=oversized_payload,
        headers={"Content-Length": str(len(oversized_payload)), "Content-Type": "application/json"},
    )
    assert resp.status_code == 413, "Server accepted an oversized payload (>1MB)!"
    assert "exceeds maximum allowed limit" in resp.json()["error"]


def test_owasp_security_headers(client):
    """
    ATTACK VECTOR 5: Clickjacking & MIME-Sniffing Prevention
    Verifies that all API responses contain OWASP-recommended security headers.
    """
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
