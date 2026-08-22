# Empirical Evaluation & Uplift Benchmarks

## 1. Experimental Methodology

To rigorously validate RIO without data leakage:
- **Dataset**: 5,000 synthetic transactions generated across 500 customers and 9 months with realistic failure distributions and ground truth counterfactual potential outcomes.
- **Temporal Splitting**:
  - Train: 70% (3,888 transactions)
  - Validation: 15% (574 transactions)
  - Held-out Test: 15% (538 transactions) — *Zero model tuning conducted on test set.*

---

## 2. Benchmark Comparison on 100% Held-Out Test Set

| Metric | Control Group (Heuristic: Retry Once) | Treatment Group (AI Intervention Optimizer) | Delta / Business Impact |
|---|---|---|---|
| **Sample Size** | 538 transactions | 538 transactions | — |
| **Total Revenue At Risk** | ₹42,38,170 | ₹42,38,170 | — |
| **Recovery Rate** | 55.2% (297 recovered) | **60.0% (323 recovered)** | **+4.8% pts** |
| **Gross Recovered Revenue** | ₹23,73,270 | **₹27,71,310** | **+₹3,98,040** |
| **Intervention & Discount Cost** | ₹5,380 | **₹32,598** | ₹27,218 |
| **Net Revenue Recovered** | ₹23,67,890 | **₹27,38,712** | **+₹3,70,822 (+15.7% net uplift)** |
| **95% Bootstrap Confidence Interval** | — | — | **[₹56,019, ₹6,68,189]** |
| **DO NOTHING Selected** | 0 (Blind retry) | **28 (5.2%)** | **Saved ₹14,200 margin** |

---

## 3. Intervention Distribution Under AI Policy

In the AI treatment group:
- **Targeted Discount (5%)**: 155 transactions (28.8%) — Price-sensitive segments with high recovery elasticity.
- **Payment Link**: 139 transactions (25.8%) — High-value VIP orders where auth failed or friction occurred.
- **Automated Retry**: 126 transactions (23.4%) — Transient network errors.
- **SMS / WhatsApp Reminder**: 90 transactions (16.7%) — Cart abandonment and low friction reminders.
- **DO NOTHING**: 28 transactions (5.2%) — Cases where natural baseline recovery was high enough that interventions or discounts destroyed net margin.
