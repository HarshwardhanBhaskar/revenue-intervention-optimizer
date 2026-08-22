# Empirical Evaluation Results: Revenue Intervention Optimizer

> **Evaluation conducted on the 100% held-out test set (538 transactions, INR 4,238,170 at risk).**
> Ground truth potential outcomes evaluated counterfactually against control.

---

## 1. Executive Summary

| Metric | Control (Rule Baseline: Retry Once) | Treatment (AI Intervention Optimizer) | Delta / Uplift |
|---|---|---|---|
| **Recovery Rate** | 55.2% | 60.0% | **+4.8% pts** |
| **Gross Recovered Revenue** | ₹2,373,270 | ₹2,771,310 | **+₹398,040** |
| **Intervention & Discount Cost** | ₹5,380 | ₹32,598 | ₹27,218 |
| **Net Revenue Recovered** | ₹2,367,890 | ₹2,738,712 | **+₹370,822 (+15.7%)** |
| **95% Confidence Interval** | — | — | **[₹56,019, ₹668,189]** |

---

## 2. Differentiated Behavior: "DO NOTHING" Selection

The AI selected **DO_NOTHING** for **28 out of 538 (5.2%)** payment failures where:
1. Natural baseline recovery was already high (no intervention waste).
2. The cost of intervention or margin dilution of a discount outweighed expected recovery uplift.
3. Policy constraints (dispute, opt-out, contact frequency) safely blocked automated recovery.

### Action Distribution on Test Set
- **DISCOUNT**: 155 transactions (28.8%)
- **PAYMENT_LINK**: 139 transactions (25.8%)
- **RETRY**: 126 transactions (23.4%)
- **REMINDER**: 90 transactions (16.7%)
- **DO_NOTHING**: 28 transactions (5.2%)

---

## 3. Methodology & Reproducibility

- **Model**: T-Learner meta-learner combining per-action Calibrated Gradient Boosting Classifiers.
- **Decision Engine**: Maximizes `IncrementalNetValue = E[Revenue|Action] - Cost(Action) - E[Revenue|DO_NOTHING]`.
- **Policy Engine**: Server-side deterministic guardrails enforced before any execution.
- **Statistical Rigor**: 1,000 bootstrap iterations for uncertainty bounds without claiming causal certainty beyond the experimental design.
