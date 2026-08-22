"""
Backend ML Model Registry & Inference Service.

Loads trained models from ml/models/ and provides real-time probability
predictions for all recovery actions for a given payment failure.
"""

from pathlib import Path
import json
import joblib
import pandas as pd
from typing import Optional

from events.event_types import ActionType
from ml.feature_engineering import FeatureEngineer, FEATURE_COLUMNS


class ModelRegistry:
    """Singleton model registry for real-time inference."""

    _instance: Optional["ModelRegistry"] = None

    def __init__(self, models_dir: Optional[Path] = None):
        if models_dir is None:
            # Default to ../ml/models relative to backend directory or root
            models_dir = Path(__file__).resolve().parent.parent.parent / "ml" / "models"
        self.models_dir = Path(models_dir)
        self.models: dict[str, any] = {}
        self.metadata: dict = {}
        self.is_loaded = False
        self._load_models()

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_models(self):
        """Load trained models from disk."""
        meta_path = self.models_dir / "metadata.json"
        if not meta_path.exists():
            print(f"[WARN] Model metadata not found at {meta_path}. Running in fallback mode.")
            return

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        actions = self.metadata.get("actions", ["do_nothing", "retry", "payment_link", "reminder", "discount"])
        for act in actions:
            model_file = self.models_dir / f"model_{act}.joblib"
            if model_file.exists():
                self.models[act] = joblib.load(model_file)

        self.is_loaded = len(self.models) == len(actions)
        if self.is_loaded:
            print(f"[OK] ModelRegistry loaded {len(self.models)} action models.")

    def predict_action_probabilities(
        self,
        transaction_dict: dict,
        customer_dict: dict,
        retry_count: int = 0,
    ) -> dict[ActionType, float]:
        """
        Predict P(recovery | action) for all possible recovery actions.
        Returns a mapping from ActionType to predicted probability.
        """
        if not self.is_loaded:
            # Safe heuristics fallback if models not loaded
            return {
                ActionType.DO_NOTHING: 0.30,
                ActionType.RETRY: 0.50,
                ActionType.PAYMENT_LINK: 0.65,
                ActionType.REMINDER: 0.40,
                ActionType.DISCOUNT: 0.70,
            }

        # Build feature vector
        X_feat = FeatureEngineer.extract_features_single(
            transaction_dict=transaction_dict,
            customer_dict=customer_dict,
            retry_count=retry_count,
        )

        results: dict[ActionType, float] = {}
        for action_name, model in self.models.items():
            prob = float(model.predict_proba(X_feat)[0, 1])
            results[ActionType(action_name)] = round(prob, 4)

        return results
