"""
Model Training Script — T-Learner Meta-Learner for Uplift & Recovery Estimation

Trains separate calibrated Gradient Boosting models for each recovery action:
- do_nothing (baseline counterfactual)
- retry
- payment_link
- reminder
- discount

Saves trained artifacts into ml/models/
"""

import sys
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

# Add project root and ml directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from feature_engineering import FeatureEngineer, FEATURE_COLUMNS


DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
ACTIONS = ["do_nothing", "retry", "payment_link", "reminder", "discount"]


def train_models():
    print("=" * 60)
    print("Training T-Learner Uplift Models")
    print("=" * 60)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    print("\n[1/4] Loading training & validation data...")
    customers_df = pd.read_csv(DATA_DIR / "raw" / "customers.csv")
    
    train_tx = pd.read_csv(DATA_DIR / "splits" / "train" / "transactions.csv")
    train_obs = pd.read_csv(DATA_DIR / "splits" / "train" / "observed.csv")
    train_merged = train_tx.merge(train_obs, on="transaction_id")

    val_tx = pd.read_csv(DATA_DIR / "splits" / "validation" / "transactions.csv")
    val_obs = pd.read_csv(DATA_DIR / "splits" / "validation" / "observed.csv")
    val_merged = val_tx.merge(val_obs, on="transaction_id")

    print(f"  -> Train samples: {len(train_merged)}")
    print(f"  -> Validation samples: {len(val_merged)}")

    # 2. Extract features
    print("\n[2/4] Extracting features...")
    X_train_all = FeatureEngineer.extract_features_df(train_tx, customers_df)
    X_val_all = FeatureEngineer.extract_features_df(val_tx, customers_df)

    trained_models = {}
    model_metrics = {}

    # 3. Train per-action models
    print("\n[3/4] Fitting calibrated models per action...")
    for action in ACTIONS:
        print(f"\n--- Action: {action.upper()} ---")
        
        # Filter training data for this action
        train_mask = train_merged["action_taken"] == action
        X_tr = X_train_all[train_mask]
        y_tr = train_merged.loc[train_mask, "payment_success"].values

        val_mask = val_merged["action_taken"] == action
        X_v = X_val_all[val_mask]
        y_v = val_merged.loc[val_mask, "payment_success"].values

        print(f"  Training samples: {len(X_tr)} (Positives: {y_tr.sum()} / {len(y_tr)})")

        # Base Estimator: Gradient Boosting Classifier
        base_gbm = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.8,
            random_state=42,
        )

        # Wrap in Isotonic Calibration
        calibrated_model = CalibratedClassifierCV(
            estimator=base_gbm,
            method="isotonic",
            cv=3,
        )
        calibrated_model.fit(X_tr, y_tr)

        # Validation metrics
        if len(X_v) > 0 and len(np.unique(y_v)) > 1:
            val_preds_prob = calibrated_model.predict_proba(X_v)[:, 1]
            auc = roc_auc_score(y_v, val_preds_prob)
            brier = brier_score_loss(y_v, val_preds_prob)
            loss = log_loss(y_v, val_preds_prob)
            print(f"  Validation AUC:   {auc:.4f}")
            print(f"  Brier score:      {brier:.4f} (lower is better)")
            print(f"  Log loss:         {loss:.4f}")
            model_metrics[action] = {
                "val_auc": round(float(auc), 4),
                "val_brier": round(float(brier), 4),
                "val_log_loss": round(float(loss), 4),
                "train_samples": int(len(X_tr)),
            }
        else:
            model_metrics[action] = {"train_samples": int(len(X_tr))}

        trained_models[action] = calibrated_model
        
        # Save model
        joblib.dump(calibrated_model, MODELS_DIR / f"model_{action}.joblib")

    # 4. Save metadata & feature list
    print("\n[4/4] Saving model registry metadata...")
    registry_meta = {
        "version": "1.0.0",
        "feature_columns": FEATURE_COLUMNS,
        "actions": ACTIONS,
        "metrics": model_metrics,
        "algorithm": "CalibratedClassifierCV(GradientBoostingClassifier, method='isotonic')",
    }
    with open(MODELS_DIR / "metadata.json", "w") as f:
        json.dump(registry_meta, f, indent=2)

    print(f"\n[OK] All {len(ACTIONS)} models saved to {MODELS_DIR}")
    return trained_models, registry_meta


if __name__ == "__main__":
    train_models()
