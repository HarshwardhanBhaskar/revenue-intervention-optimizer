# AI & Machine Learning Architecture — Revenue Intervention Optimizer

## 1. Why AI vs Why Deterministic Logic?

Fintech applications require rigorous boundaries on probabilistic intelligence:

| Subsystem | Approach | Rationale |
|---|---|---|
| **Intervention Outcome Estimation** | **Machine Learning (T-Learner)** | Estimating individual treatment effects across complex multi-variable interactions (customer segment, failure reason, method, past frequency) cannot be hand-coded as static rules. |
| **Financial Policy Enforcement** | **Deterministic Backend Code** | Rules such as *"Never discount more than 5%"* or *"Block interventions on active chargebacks"* must have **zero variance** and 100% testable guarantees. |
| **Payment Link Execution** | **Deterministic Backend Code** | Idempotency, HMAC verification, and monetary amounts require deterministic server execution. |
| **State Machine & Workflows** | **Deterministic State Graph** | Transitioning from `PENDING_APPROVAL` to `APPROVED` requires strict optimistic concurrency guards. |
| **Operational Q&A (Analyst)** | **Grounded LLM Query Engine** | Translates natural language questions into structured SQL/ledger aggregations, citing live metrics without hallucination. |

---

## 2. Causal Uplift Modeling: The T-Learner Framework

Standard classification models estimate $P(Y=1 \mid X)$, which answers *"Will this customer pay?"* (favoring high-intent customers who would pay anyway).

RIO uses a **T-Learner (Treatment Learner)** uplift meta-algorithm. We train 5 distinct, well-calibrated Gradient Boosting estimators:

$$\mu_0(X) = P(Y=1 \mid X, W=\text{do\_nothing})$$
$$\mu_1(X) = P(Y=1 \mid X, W=\text{retry})$$
$$\mu_2(X) = P(Y=1 \mid X, W=\text{payment\_link})$$
$$\mu_3(X) = P(Y=1 \mid X, W=\text{reminder})$$
$$\mu_4(X) = P(Y=1 \mid X, W=\text{discount})$$

### Conditional Average Treatment Effect (CATE)
$$\tau_a(X) = \mu_a(X) - \mu_0(X)$$

### Probability Calibration
Raw Gradient Boosting Classifiers output uncalibrated scores. We wrap each sub-model in `CalibratedClassifierCV(method='isotonic')` to ensure that predicted probabilities represent true empirical frequencies—a strict requirement for economic expected value calculations.

---

## 3. Mathematical Economic Value Function

For any candidate action $a \in \{\text{do\_nothing}, \text{retry}, \text{payment\_link}, \text{reminder}, \text{discount}\}$:

$$\mathbb{E}[\text{NetValue}(a)] = \mu_a(X) \times \text{Amount} - \text{Cost}(a) - \text{DiscountCost}(a, X)$$

Where:
- $\text{Cost}(\text{do\_nothing}) = 0$
- $\text{Cost}(\text{retry}) = \text{₹10 (network gateway fee)}$
- $\text{Cost}(\text{payment\_link}) = \text{₹20 (gateway link creation)}$
- $\text{Cost}(\text{reminder}) = \text{₹5 (SMS / WhatsApp notification cost)}$
- $\text{Cost}(\text{discount}) = \text{₹20} + (\mu_{\text{discount}}(X) \times \text{Amount} \times \text{DiscountRate})$

### The Incremental Decision Rule
$$\text{IncrementalNetValue}(a) = \mathbb{E}[\text{NetValue}(a)] - \mathbb{E}[\text{NetValue}(\text{do\_nothing})]$$

$$a^* = \arg\max_{a} \text{IncrementalNetValue}(a)$$

If $\max_a \text{IncrementalNetValue}(a) < \text{MinThreshold}$, the system chooses **`DO_NOTHING`**.
