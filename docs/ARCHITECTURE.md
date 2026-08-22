# System Architecture — Revenue Intervention Optimizer (RIO)

## 1. System Overview

RIO is a production-grade fintech intelligence engine designed to maximize **incremental net revenue** from payment failures rather than raw intervention volume. It implements an explicit, bounded 11-stage loop:

```
DETECT → UNDERSTAND → PREDICT → SIMULATE → DECIDE → POLICY CHECK → HUMAN APPROVAL IF REQUIRED → EXECUTE → OBSERVE → MEASURE → LEARN
```

---

## 2. Component Topology

```mermaid
flowchart TD
    subgraph Ingestion ["1. Webhook Ingestion & Deduplication"]
        RZP_WH["Razorpay Webhook (payment.failed)"] --> HMAC["HMAC-SHA256 Signature Validator"]
        HMAC --> DEDUP["Idempotency Filter (PaymentEvent unique key)"]
    end

    subgraph FeatureML ["2. Causal Uplift & Machine Learning"]
        DEDUP --> FEAT["Feature Engineering (26 tabular signals, zero outcome leakage)"]
        FEAT --> T_LEARNER["T-Learner Meta-Learner (5 Calibrated GBMs)"]
        T_LEARNER --> DECISION["Economic Decision Engine (Argmax Incremental Net Value)"]
    end

    subgraph Guardrails ["3. Deterministic Safety & Authorization"]
        DECISION --> FIREWALL["Risk Firewall (Fraud, Concurrency, Model Availability)"]
        FIREWALL --> POLICY["Policy Engine (Deterministic Limits, Opt-Out, Disputes)"]
        POLICY -->|Amount > ₹10,000| APPROVAL["Approval Queue (Operator Sign-off)"]
        POLICY -->|Opt-Out / Disputed| BLOCK["Safe DO NOTHING Fallback"]
        POLICY -->|Approved| WORKFLOW["Workflow State Machine"]
        APPROVAL -->|Operator Approve| WORKFLOW
        APPROVAL -->|Operator Reject| BLOCK
    end

    subgraph Execution ["4. Execution & Audit"]
        WORKFLOW --> EXEC["Razorpay Client Wrapper (Payment Links / Retries)"]
        EXEC --> OUTCOME["Payment Capture / Expiry Observer"]
        OUTCOME --> AUDIT["Append-Only Immutable Event Ledger"]
    end
```

---

## 3. Database Schema Design (PostgreSQL / SQLite)

The database schema guarantees strict referential integrity and prevents floating-point monetary discrepancies by using **integer paise** across all financial fields.

```mermaid
erDiagram
    MERCHANT ||--o{ USER : has
    MERCHANT ||--o{ CUSTOMER : has
    MERCHANT ||--o{ POLICY : configures
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ PAYMENT : attempts
    PAYMENT ||--o{ RECOVERY_OPPORTUNITY : triggers
    RECOVERY_OPPORTUNITY ||--o{ RECOVERY_ACTION : generates
    RECOVERY_ACTION ||--o{ RECOVERY_OUTCOME : produces
    RECOVERY_OPPORTUNITY ||--o{ AUDIT_EVENT : records
```

---

## 4. Separation of Concerns & Authority Hierarchy

| Component | Responsibility | Authority Level | Technology |
|---|---|---|---|
| **T-Learner ML Models** | Estimate conditional recovery probabilities per action: $P(\text{Recovery} \mid X, a)$ | Advisory Only | Scikit-Learn `CalibratedClassifierCV` |
| **Economic Decision Engine** | Calculate net values and rank actions: $\text{Argmax} [\mathbb{E}[\text{Net} \mid a] - \mathbb{E}[\text{Net} \mid \text{do-nothing}]]$ | Recommendation | Python Domain Service |
| **Risk Firewall** | Pre-policy circuit breaker (fraud, missing models, race guards) | Deterministic Hard Gate | Python Domain Service |
| **Policy Engine** | Business rules enforcement (₹10k threshold, 5% max discount, opt-out, disputes) | Deterministic Authoritative | Python Domain Service |
| **State Machine** | Validates legal transitions (`DETECTED` $\to$ `ANALYZING` $\to \dots \to$ `RECOVERED`) | State Authority | Python Enum & Guard Rules |
| **Audit Engine** | Event-sourced append-only ledger | Immutable Record | Async SQLAlchemy Event Log |
| **Next.js Web UI** | Presentation and operator interaction | Read-only / Untrusted | Next.js 14 App Router |
