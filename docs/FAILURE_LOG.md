# Failure Scenarios & Edge Cases Tested

The Revenue Intervention Optimizer is built around the fundamental philosophy that **a financial system's quality is defined by how safely it behaves under failure**.

---

## 1. Safety & Guardrail Failure Modes

| Scenario | Condition | System Behavior | Audit Trail Event |
|---|---|---|---|
| **Customer Communication Opt-Out** | Customer previously requested no marketing/comms (`opted_out = True`) | `PolicyEngine` blocks `REMINDER`, `PAYMENT_LINK`, and `DISCOUNT`. System safely falls back to `DO_NOTHING` or gateway-level silent retry. | `recovery.blocked` with reason `customer_opt_out` |
| **Active Dispute / Chargeback** | Customer has a pending dispute (`has_active_dispute = True`) | `PolicyEngine` enforces a complete block on all recovery actions to prevent escalating merchant chargeback penalties. | `recovery.blocked` with reason `active_dispute` |
| **High-Value Transaction Threshold** | Transaction amount > `human_approval_threshold` (₹10,000) | `RecoveryEngine` shifts state to `PENDING_APPROVAL` and queues transaction in the Operator Approval Queue. | `recovery.approval_requested` |
| **Max Retry Limit Exceeded** | `retry_count >= max_retry_attempts` (2 retries) | Further retry attempts are blocked to prevent card network fatigue fees and customer friction. | `recovery.blocked` with reason `max_retry_attempts` |
| **Margin Dilution from Excess Discount** | Model predicts discount gives highest recovery, but discount cost > expected incremental revenue | Economic value function computes negative incremental yield: `IncrementalNet < min_threshold` → System selects `DO_NOTHING`. | `recovery.recommended` with action `do_nothing` |

---

## 2. Distributed Systems & Reliability Failures

| Scenario | Failure Mode | Resilience Mechanism | Verification Test |
|---|---|---|---|
| **Duplicate Webhook Delivery** | Razorpay sends same `payment.failed` webhook twice due to network timeout | Event deduplication via `idempotency_key = "wh_" + event_id` in PostgreSQL / SQLite unique constraint. Second delivery returns 200 `duplicate_ignored`. | `test_webhook_ingestion_and_deduplication` in integration suite |
| **Concurrent Approval Race** | Two operators attempt to approve the same pending opportunity simultaneously | Optimistic state transition validation: transition from `PENDING_APPROVAL` to `APPROVED` succeeds only once. Second attempt returns HTTP 409 Conflict. | `test_pending_approvals_and_action_flow` |
| **ML Model Service Unavailable** | Model weights or prediction pipeline error | `RiskFirewall` detects missing predictions and safely escalates to `ESCALATE` / human review or safe fallback rule without crashing. | `RiskFirewall.evaluate(model_available=False)` |
| **Razorpay API Downtime** | Network error when calling Razorpay Payment Link API | Fallback simulated mode with unique reference IDs and logged retry metadata without losing state. | `RazorpayClientWrapper` simulation handler |
