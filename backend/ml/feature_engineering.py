"""
Feature Engineering Pipeline — Backend ML package.
"""

from typing import Any
import pandas as pd
import numpy as np


FEATURE_COLUMNS = [
    "amount_log",
    "amount_normalized",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "historical_orders",
    "historical_success_rate",
    "historical_recovery_rate",
    "opted_out",
    "has_active_dispute",
    # One-hot encoded customer segments
    "segment_premium",
    "segment_loyal",
    "segment_regular",
    "segment_price_sensitive",
    "segment_new",
    # One-hot encoded failure reasons
    "reason_insufficient_funds",
    "reason_network_error",
    "reason_authentication_failed",
    "reason_card_expired",
    "reason_bank_declined",
    "reason_timeout",
    # One-hot encoded payment methods
    "method_upi",
    "method_credit_card",
    "method_debit_card",
    "method_netbanking",
    # Retry state
    "retry_count",
]


class FeatureEngineer:
    """Extracts features for ML model training and inference."""

    @staticmethod
    def extract_features_df(
        transactions_df: pd.DataFrame,
        customers_df: pd.DataFrame,
        retry_counts: pd.Series | None = None,
    ) -> pd.DataFrame:
        """
        Merge transaction and customer data and build feature matrix.
        No target outcome columns are included.
        """
        merged = transactions_df.merge(customers_df, on="customer_id", how="left")

        df_feat = pd.DataFrame(index=merged.index)

        # Monetary features
        amount = merged["amount"].astype(float)
        df_feat["amount_log"] = np.log1p(amount)
        df_feat["amount_normalized"] = (amount - 200.0) / (50000.0 - 200.0)

        # Time features
        df_feat["hour_of_day"] = merged["hour_of_day"].astype(int)
        df_feat["day_of_week"] = merged["day_of_week"].astype(int)
        df_feat["is_weekend"] = (merged["day_of_week"] >= 5).astype(int)

        # Customer behavior
        df_feat["historical_orders"] = merged["historical_orders"].fillna(0).astype(int)
        df_feat["historical_success_rate"] = merged["success_rate"].fillna(0.7).astype(float)
        df_feat["historical_recovery_rate"] = merged["historical_recovery_rate"].fillna(0.3).astype(float)
        df_feat["opted_out"] = merged["opted_out"].fillna(False).astype(int)
        df_feat["has_active_dispute"] = merged["has_active_dispute"].fillna(False).astype(int)

        # Segments
        for seg in ["premium", "loyal", "regular", "price_sensitive", "new"]:
            df_feat[f"segment_{seg}"] = (merged["segment"] == seg).astype(int)

        # Failure reasons
        for reason in [
            "insufficient_funds",
            "network_error",
            "authentication_failed",
            "card_expired",
            "bank_declined",
            "timeout",
        ]:
            df_feat[f"reason_{reason}"] = (merged["failure_reason"] == reason).astype(int)

        # Payment methods
        for method in ["upi", "credit_card", "debit_card", "netbanking"]:
            df_feat[f"method_{method}"] = (merged["payment_method"] == method).astype(int)

        # Retry count
        if retry_counts is not None:
            df_feat["retry_count"] = retry_counts.values
        elif "retry_count" in merged.columns:
            df_feat["retry_count"] = merged["retry_count"].fillna(0).astype(int)
        else:
            df_feat["retry_count"] = 0

        # Ensure all expected columns are present
        for col in FEATURE_COLUMNS:
            if col not in df_feat.columns:
                df_feat[col] = 0

        return df_feat[FEATURE_COLUMNS]

    @staticmethod
    def extract_features_single(
        transaction_dict: dict[str, Any],
        customer_dict: dict[str, Any],
        retry_count: int = 0,
    ) -> pd.DataFrame:
        """Extract features for a single runtime transaction."""
        tx_dict = dict(transaction_dict)
        cust_dict = dict(customer_dict)
        dummy_cid = "runtime_cust_0"
        tx_dict["customer_id"] = dummy_cid
        cust_dict["customer_id"] = dummy_cid
        tx_df = pd.DataFrame([tx_dict])
        cust_df = pd.DataFrame([cust_dict])
        tx_df["retry_count"] = retry_count
        return FeatureEngineer.extract_features_df(tx_df, cust_df)
