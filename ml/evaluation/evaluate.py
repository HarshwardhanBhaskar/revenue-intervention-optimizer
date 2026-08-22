"""
Comprehensive Evaluation & Experiment Benchmark Script

Evaluates:
1. Control: Baseline Policy (Always retry once)
2. Treatment: AI Intervention Optimizer (T-Learner CATE estimation + Economic Ranking)

Evaluates on the held-out test set using ground-truth potential outcomes:
- Recovery rate
- Gross recovered revenue
- Intervention cost (gateway fees + discounts)
- Net revenue recovered
- Incremental net revenue recovered vs baseline
- Confidence intervals via bootstrap (1000 resamples)
- Per-action distribution & DO_NOTHING frequency

Exports evaluation metrics to JSON and Markdown.
"""

import sys
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from feature_engineering import FeatureEngineer
from domain.decision_engine import DecisionEngine, DEFAULT_ACTION_COSTS
from domain.policy_engine import PolicyEngine, PolicyConfig, RecoveryContext, RecommendedAction
from events.event_types import ActionType


DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
DOCS_DIR = PROJECT_ROOT / "docs"
ACTIONS = ["do_nothing", "retry", "payment_link", "reminder", "discount"]


def evaluate_test_set():
    print("=" * 60)
    print("Revenue Intervention Optimizer — Held-Out Test Set Benchmark")
    print("=" * 60)

    # 1. Load data & models
    test_tx = pd.read_csv(DATA_DIR / "splits" / "test" / "transactions.csv")
    customers_df = pd.read_csv(DATA_DIR / "raw" / "customers.csv")
    test_gt = pd.read_csv(DATA_DIR / "splits" / "test" / "ground_truth.csv")
    
    # Merge test data with customer data
    cust_lookup = customers_df.set_index("customer_id")
    gt_lookup = test_gt.set_index("transaction_id")

    # Load models
    models = {}
    for action in ACTIONS:
        model_path = MODELS_DIR / f"model_{action}.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file {model_path} not found. Please train models first.")
        models[action] = joblib.load(model_path)

    # Extract features for all test transactions
    X_test = FeatureEngineer.extract_features_df(test_tx, customers_df)

    # Predict probabilities for each action across all test transactions
    predictions_df = pd.DataFrame(index=test_tx.index)
    for action in ACTIONS:
        predictions_df[action] = models[action].predict_proba(X_test)[:, 1]

    # Initialize decision and policy engines
    decision_engine = DecisionEngine()
    policy_engine = PolicyEngine(PolicyConfig())

    # 2. Simulate Baseline Policy vs AI Policy on test set
    baseline_results = []
    ai_results = []

    for idx, tx in test_tx.iterrows():
        tx_id = tx["transaction_id"]
        amt = tx["amount"]
        amt_paise = tx["amount_paise"]
        gt = gt_lookup.loc[tx_id]
        customer = cust_lookup.loc[tx["customer_id"]]

        # --- BASELINE POLICY (Retry once heuristic) ---
        baseline_action = "retry"
        b_cost = DEFAULT_ACTION_COSTS[ActionType.RETRY] / 100.0  # Rs 10
        b_success = bool(gt[f"outcome_{baseline_action}"])
        b_recovered = amt if b_success else 0
        b_discount = 0.0
        b_net = b_recovered - b_cost - b_discount

        baseline_results.append({
            "transaction_id": tx_id,
            "action": baseline_action,
            "success": b_success,
            "recovered_amount": b_recovered,
            "cost": b_cost,
            "discount_cost": b_discount,
            "net_recovered": b_net,
        })

        # --- AI POLICY ---
        # Get predictions for this transaction
        preds = {
            ActionType.DO_NOTHING: float(predictions_df.loc[idx, "do_nothing"]),
            ActionType.RETRY: float(predictions_df.loc[idx, "retry"]),
            ActionType.PAYMENT_LINK: float(predictions_df.loc[idx, "payment_link"]),
            ActionType.REMINDER: float(predictions_df.loc[idx, "reminder"]),
            ActionType.DISCOUNT: float(predictions_df.loc[idx, "discount"]),
        }

        # Decision engine ranks actions
        ranking = decision_engine.evaluate_actions(
            amount_paise=amt_paise,
            predictions=preds,
            min_incremental_value_paise=10_000,  # Min INR 100 incremental value
        )
        ai_action_type = ranking.recommended_action or ActionType.DO_NOTHING
        
        # Policy & Risk check
        rec_action = RecommendedAction(
            action_type=ai_action_type,
            expected_incremental_value_paise=ranking.recommended_incremental_value_paise,
            discount_percentage=5.0 if ai_action_type == ActionType.DISCOUNT else 0.0,
        )
        ctx = RecoveryContext(
            amount_paise=amt_paise,
            customer_opted_out=bool(customer["opted_out"]),
            customer_has_dispute=bool(customer["has_active_dispute"]),
        )
        policy_res = policy_engine.evaluate(rec_action, ctx)

        if policy_res.is_blocked:
            final_action_str = "do_nothing"
        else:
            final_action_str = ai_action_type.value

        # Ground truth outcome for the chosen AI action
        ai_success = bool(gt[f"outcome_{final_action_str}"])
        ai_cost = DEFAULT_ACTION_COSTS[ActionType(final_action_str)] / 100.0
        ai_discount = (amt * 0.05) if (final_action_str == "discount" and ai_success) else 0.0
        ai_recovered = amt if ai_success else 0
        ai_net = ai_recovered - ai_cost - ai_discount

        ai_results.append({
            "transaction_id": tx_id,
            "action": final_action_str,
            "success": ai_success,
            "recovered_amount": ai_recovered,
            "cost": ai_cost,
            "discount_cost": ai_discount,
            "net_recovered": ai_net,
        })

    df_b = pd.DataFrame(baseline_results)
    df_ai = pd.DataFrame(ai_results)

    # 3. Aggregate Metrics
    n_tx = len(test_tx)
    total_at_risk = test_tx["amount"].sum()

    # Baseline Aggregates
    b_rec_rate = df_b["success"].mean()
    b_gross_rec = df_b["recovered_amount"].sum()
    b_total_cost = df_b["cost"].sum() + df_b["discount_cost"].sum()
    b_net_rec = df_b["net_recovered"].sum()

    # AI Aggregates
    ai_rec_rate = df_ai["success"].mean()
    ai_gross_rec = df_ai["recovered_amount"].sum()
    ai_total_cost = df_ai["cost"].sum() + df_ai["discount_cost"].sum()
    ai_net_rec = df_ai["net_recovered"].sum()

    # Incremental Impact
    incremental_gross = ai_gross_rec - b_gross_rec
    incremental_net = ai_net_rec - b_net_rec
    pct_net_uplift = (incremental_net / b_net_rec) * 100 if b_net_rec > 0 else 0

    # Action breakdown for AI
    action_counts = df_ai["action"].value_counts().to_dict()
    do_nothing_count = action_counts.get("do_nothing", 0)

    # 4. Bootstrap Confidence Intervals (1000 iterations)
    np.random.seed(42)
    boot_net_diffs = []
    for _ in range(1000):
        sample_idx = np.random.choice(n_tx, size=n_tx, replace=True)
        sample_b_net = df_b.iloc[sample_idx]["net_recovered"].sum()
        sample_ai_net = df_ai.iloc[sample_idx]["net_recovered"].sum()
        boot_net_diffs.append(sample_ai_net - sample_b_net)

    ci_lower = np.percentile(boot_net_diffs, 2.5)
    ci_upper = np.percentile(boot_net_diffs, 97.5)

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS (HELD-OUT TEST SET)")
    print("=" * 60)
    print(f"Test Transactions:         {n_tx}")
    print(f"Total Revenue at Risk:     INR {total_at_risk:,.0f}")
    print("-" * 60)
    print("CONTROL (Baseline Policy - Retry Once):")
    print(f"  Recovery Rate:           {b_rec_rate:.1%}")
    print(f"  Gross Revenue Recovered: INR {b_gross_rec:,.0f}")
    print(f"  Intervention Costs:      INR {b_total_cost:,.0f}")
    print(f"  Net Revenue Recovered:   INR {b_net_rec:,.0f}")
    print("-" * 60)
    print("TREATMENT (AI Intervention Optimizer):")
    print(f"  Recovery Rate:           {ai_rec_rate:.1%}")
    print(f"  Gross Revenue Recovered: INR {ai_gross_rec:,.0f}")
    print(f"  Intervention Costs:      INR {ai_total_cost:,.0f}")
    print(f"  Net Revenue Recovered:   INR {ai_net_rec:,.0f}")
    print("-" * 60)
    print("INCREMENTAL BUSINESS IMPACT:")
    print(f"  Incremental Net Revenue: INR {incremental_net:,.0f} (+{pct_net_uplift:.1f}%)")
    print(f"  95% CI on Net Uplift:    [INR {ci_lower:,.0f}, INR {ci_upper:,.0f}]")
    print(f"  Actions Saved (DO_NOTHING): {do_nothing_count} / {n_tx} ({do_nothing_count/n_tx:.1%})")
    print("\nAction Distribution:")
    for act, cnt in action_counts.items():
        print(f"  {act:16s}: {cnt:4d} ({cnt/n_tx:.1%})")

    # 5. Export results to JSON and Markdown
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    clean_action_counts = {str(k): int(v) for k, v in action_counts.items()}

    results_json = {
        "dataset": "held-out-test-set",
        "sample_size": int(n_tx),
        "revenue_at_risk": float(total_at_risk),
        "control_baseline": {
            "policy": "retry_once",
            "recovery_rate": round(float(b_rec_rate), 4),
            "gross_recovered": float(b_gross_rec),
            "total_cost": float(b_total_cost),
            "net_recovered": float(b_net_rec),
        },
        "treatment_ai": {
            "policy": "t_learner_economic_optimization",
            "recovery_rate": round(float(ai_rec_rate), 4),
            "gross_recovered": float(ai_gross_rec),
            "total_cost": float(ai_total_cost),
            "net_recovered": float(ai_net_rec),
            "action_distribution": clean_action_counts,
            "do_nothing_rate": round(float(do_nothing_count / n_tx), 4),
        },
        "incremental_impact": {
            "incremental_gross_revenue": float(incremental_gross),
            "incremental_net_revenue": float(incremental_net),
            "percentage_uplift": round(float(pct_net_uplift), 2),
            "ci_95_lower": float(ci_lower),
            "ci_95_upper": float(ci_upper),
        },
    }

    with open(DOCS_DIR / "evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2)

    # Markdown report
    md_content = f"""# Empirical Evaluation Results: Revenue Intervention Optimizer

> **Evaluation conducted on the 100% held-out test set ({n_tx} transactions, INR {total_at_risk:,.0f} at risk).**
> Ground truth potential outcomes evaluated counterfactually against control.

---

## 1. Executive Summary

| Metric | Control (Rule Baseline: Retry Once) | Treatment (AI Intervention Optimizer) | Delta / Uplift |
|---|---|---|---|
| **Recovery Rate** | {b_rec_rate:.1%} | {ai_rec_rate:.1%} | **+{ (ai_rec_rate - b_rec_rate)*100 :.1f}% pts** |
| **Gross Recovered Revenue** | ₹{b_gross_rec:,.0f} | ₹{ai_gross_rec:,.0f} | **+₹{incremental_gross:,.0f}** |
| **Intervention & Discount Cost** | ₹{b_total_cost:,.0f} | ₹{ai_total_cost:,.0f} | ₹{ai_total_cost - b_total_cost:,.0f} |
| **Net Revenue Recovered** | ₹{b_net_rec:,.0f} | ₹{ai_net_rec:,.0f} | **+₹{incremental_net:,.0f} (+{pct_net_uplift:.1f}%)** |
| **95% Confidence Interval** | — | — | **[₹{ci_lower:,.0f}, ₹{ci_upper:,.0f}]** |

---

## 2. Differentiated Behavior: "DO NOTHING" Selection

The AI selected **DO_NOTHING** for **{do_nothing_count} out of {n_tx} ({do_nothing_count/n_tx:.1%})** payment failures where:
1. Natural baseline recovery was already high (no intervention waste).
2. The cost of intervention or margin dilution of a discount outweighed expected recovery uplift.
3. Policy constraints (dispute, opt-out, contact frequency) safely blocked automated recovery.

### Action Distribution on Test Set
"""
    for act, cnt in action_counts.items():
        md_content += f"- **{act.upper()}**: {cnt} transactions ({cnt/n_tx:.1%})\n"

    md_content += """
---

## 3. Methodology & Reproducibility

- **Model**: T-Learner meta-learner combining per-action Calibrated Gradient Boosting Classifiers.
- **Decision Engine**: Maximizes `IncrementalNetValue = E[Revenue|Action] - Cost(Action) - E[Revenue|DO_NOTHING]`.
- **Policy Engine**: Server-side deterministic guardrails enforced before any execution.
- **Statistical Rigor**: 1,000 bootstrap iterations for uncertainty bounds without claiming causal certainty beyond the experimental design.
"""

    with open(DOCS_DIR / "evaluation_results.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n[OK] Results saved to {DOCS_DIR / 'evaluation_results.json'}")
    print(f"[OK] Report saved to {DOCS_DIR / 'evaluation_results.md'}")
    return results_json


if __name__ == "__main__":
    evaluate_test_set()
