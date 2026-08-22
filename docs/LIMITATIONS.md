# System Limitations & Future Scope

In adherence to fintech engineering integrity, this document explicitly outlines the boundary conditions, synthetic assumptions, and current technical limitations of the prototype.

---

## 1. Explicit Scope & Verification Status

| Component | Status | Description |
|---|---|---|
| **Payment Link Creation** | **Real Razorpay Test Mode** | Creates real payment links via the Razorpay test API when keys are provided; falls back to deterministic simulation if keys are omitted. |
| **Webhook Ingestion** | **Real Production Code** | Full cryptographic HMAC-SHA256 signature verification and idempotency deduplication. |
| **Dataset** | **Synthetic with Ground Truth** | 5,000 transactions generated with realistic behavioral distributions to enable counterfactual evaluation. |
| **Causal Uplift Models** | **Real Trained ML Artifacts** | 5 Calibrated Gradient Boosting models trained and serialized via joblib. |
| **Policy Engine & State Machine** | **Real Deterministic Code** | 100% server-side Python domain services covered by 81 unit/integration tests. |

---

## 2. Technical Limitations

1. **Card Network Silent Retries**: In production environments, silent retries on network/timeout failures often require direct gateway routing (Smart Routing) rather than external API calls. In test mode, this is simulated via standard retry requests.
2. **Dynamic Discount Coupon Generation**: Discounts are evaluated as economic cost deductions on payment links. In a production D2C stack, this would sync with Shopify/WooCommerce coupon APIs.
3. **Temporal Drift & Online Retraining**: Current models are trained offline on historical cohorts. Future iterations would incorporate online Bayesian updating as recovery outcomes mature.
