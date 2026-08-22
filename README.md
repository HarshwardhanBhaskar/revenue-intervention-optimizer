# Revenue Intervention Optimizer (RIO)
### Track 03: AI Revenue Recovery — Razorpay AI Buildathon

> **A production-grade fintech intelligence engine that maximizes incremental net revenue, treats "DO NOTHING" as a first-class financial decision, and bounds AI with deterministic safety guardrails.**

---

## 1. The Core Product Thesis

Traditional recovery systems blindly retry every failed transaction or spam reminders. In contrast, **RIO** evaluates every payment failure counterfactually across 5 potential actions (`DO_NOTHING`, `RETRY`, `PAYMENT_LINK`, `REMINDER`, `DISCOUNT`) to maximize:

$$\text{IncrementalNetValue}(a) = \mathbb{E}[\text{Revenue} \mid a] - \text{Cost}(a) - \text{DiscountCost}(a) - \mathbb{E}[\text{Revenue} \mid \text{DO\_NOTHING}]$$

```
DETECT → UNDERSTAND → PREDICT → SIMULATE → DECIDE → POLICY CHECK → HUMAN APPROVAL IF REQUIRED → EXECUTE → OBSERVE → MEASURE → LEARN
```

---

## 2. Empirical Benchmark Results (100% Held-Out Test Set)

Evaluated across **538 test transactions (₹42.38L at risk)**:

| Metric | Control Group (Rule Baseline: Retry Once) | Treatment Group (AI Intervention Optimizer) | Delta / Business Impact |
|---|---|---|---|
| **Recovery Rate** | 55.2% | **60.0%** | **+4.8% pts** |
| **Gross Recovered Revenue** | ₹23,73,270 | **₹27,71,310** | **+₹3,98,040** |
| **Intervention & Discount Cost** | ₹5,380 | **₹32,598** | ₹27,218 |
| **Net Revenue Recovered** | ₹23,67,890 | **₹27,38,712** | **+₹3,70,822 (+15.7% net uplift)** |
| **95% Bootstrap Confidence Interval** | — | — | **[₹56,019, ₹6,68,189]** |
| **DO NOTHING Frequency** | 0% (Blind retry) | **5.2% (28 transactions)** | **Saved ₹14,200 in wasted margin** |

---

## 3. Application Information Architecture & Key Screens

| Route | Screen Name | Key Operational Functionality |
|---|---|---|
| `/` | **Landing Page** | Editorial statement, particle/dither canvas, 11-stage loop, and empirical metrics. |
| `/login` | **Login** | Editorial split-layout operator authentication. |
| `/overview` | **Control Center** | Financial impact headline, Recovery Signal Grid (interactive layout grid), and trajectory charts. |
| `/recovery` | **Opportunities Ledger** | Dense financial operations table, multi-filter, search, and server-side pagination. |
| `/recovery/[id]` | **Decision Inspection Detail** | 5-action counterfactual comparison, policy checklist, and *Why this action? / Why not alternatives?* rationale. |
| `/decision-lab` | **Decision Lab** *(Signature)* | Live what-if parameter sliders, discount sensitivity curves, and dynamic argmax recalculations. |
| `/experiments` | **Experiments & Benchmarks** | Control vs Treatment empirical benchmarks with 1,000 bootstrap iterations. |
| `/approvals` | **Human Approval Queue** | Operator sign-off for transactions >₹10,000 with concurrency-safe Approve/Reject. |
| `/exceptions` | **Exceptions & Guardrails** | System exceptions, opt-out enforcement blocks, and circuit-breaker history. |
| `/policies` | **Policy Center** | Merchant-configurable financial limits with append-only audited updates. |
| `/audit` | **Audit Log** | Immutable event stream with searchable event types and JSON payload inspector. |
| `/analyst` | **AI Revenue Analyst** | Conversational investigation grounded strictly in live database records. |
| `/settings` | **Merchant Settings** | Gateway credentials, Razorpay test mode keys, and webhook secret management. |

---

## 4. Engineering & Safety Highlights
- **Paise Precision**: All monetary values are represented as integer paise internally to prevent IEEE 754 floating-point errors.
- **Deterministic Guardrails**: Financial policies and payment executions are 100% deterministic Python services. LLMs never have financial execution authority.
- **HMAC-SHA256 & Idempotency**: Webhook signatures are verified cryptographically; duplicate event IDs return HTTP 200 `duplicate_ignored` with zero duplicate side effects.
- **81 Automated Tests Passing**: Comprehensive unit and integration test coverage across decision engine, policy rules, and API endpoints.

---

## 5. Quickstart & Local Execution

### Prerequisites
- Python 3.11+
- Node.js 18+

### Step 1: Start Backend
```powershell
cd revenue-intervention-optimizer\backend
..\backend\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Step 2: Start Frontend
```powershell
cd revenue-intervention-optimizer\frontend
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### Step 3: Run Full Test Suite
```powershell
cd revenue-intervention-optimizer
.\backend\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 6. Comprehensive Documentation Index
- 📘 [System Architecture](docs/ARCHITECTURE.md)
- 🧠 [AI & Causal Uplift Architecture](docs/AI_ARCHITECTURE.md)
- 🔒 [Security & Idempotency Specifications](docs/SECURITY.md)
- 📊 [Empirical Evaluation Report](docs/EVALUATION.md)
- 🛠️ [Failure Recovery Log & Incidents](docs/FAILURE_RECOVERY.md)
- 🎙️ [5-Minute Demo Presentation Script](docs/DEMO.md)
- ⚠️ [Limitations & Boundary Conditions](docs/LIMITATIONS.md)
