# Security & Financial Integrity Specifications

## 1. Zero Trust Frontend Architecture

The web frontend is treated as an untrusted presentation layer:
- **No Financial Math on Client**: All probability rankings, net revenue calculations, and discount determinations occur strictly on the backend.
- **No Direct Execution**: The frontend cannot dispatch payment links directly; it can only submit signed approval/reject requests that validate transition preconditions in PostgreSQL.
- **Server-Side Policy Enforcement**: Policy limits (such as ₹10,000 human thresholds or 5% discount caps) cannot be overridden via frontend payload tampering.

---

## 2. Webhook Authentication & Idempotency

1. **HMAC-SHA256 Signature Verification**:
   - Every incoming Razorpay webhook payload is validated against the merchant's secret key:
     $$\text{Signature} = \text{HMAC-SHA256}(\text{raw-payload}, \text{secret})$$
   - Invalid signatures are rejected with HTTP 400 immediately.

2. **Event Deduplication (Idempotency Ledger)**:
   - Webhooks are recorded in the `PaymentEvent` table with a unique constraint on `idempotency_key = "wh_" + event_id`.
   - Repeated webhook deliveries return HTTP 200 `duplicate_ignored` with zero duplicate side effects.

---

## 3. Financial Numerical Safety

- **Integer Paise Representation**: All monetary quantities are stored and manipulated as 64-bit integer paise (1 INR = 100 paise) across database tables, domain entities, and API schemas to eliminate floating-point rounding errors.
- **Optimistic Concurrency Guards**: Action approvals verify that `workflow_state == PENDING_APPROVAL` in an atomic database transaction, preventing double-approval race conditions.
