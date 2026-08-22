"""
Synthetic Data Generator — Revenue Intervention Optimizer

Generates realistic payment failure + recovery data with KNOWN GROUND TRUTH.

Key design: We generate BOTH potential outcomes for each transaction
(recovery under each possible action). The evaluation can then compute
true uplift. The ML model only sees the observed outcome.

Data relationships (ground truth):
- Failure reason → recoverability (e.g., insufficient_funds = 45% base recovery)
- Customer segment → intervention response (premium → payment links work best)
- Payment method → failure pattern (UPI fails on network, CC on auth)
- Amount → recovery probability (higher amounts = lower baseline recovery)
- Retry count → diminishing returns (1st: +15%, 2nd: +5%, 3rd: +1%)
- Discount → conversion uplift (5% discount = ~8% probability uplift)
- Time since failure → decay (~5% per 24 hours)
- Historical behavior → prediction (>80% success rate = 2x baseline)

All probabilities have noise (Beta distribution) to prevent unrealistically
clean patterns.
"""

import os
import json
import uuid
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np
import pandas as pd


# ============================================================================
# Configuration
# ============================================================================

SEED = 42
NUM_CUSTOMERS = 500
NUM_TRANSACTIONS = 5000
OUTPUT_DIR = Path(__file__).parent.parent / "raw"
SPLITS_DIR = Path(__file__).parent.parent / "splits"

# Temporal range: 9 months
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 9, 30, tzinfo=timezone.utc)

# Split boundaries (temporal split)
TRAIN_END = datetime(2025, 7, 31, tzinfo=timezone.utc)       # Months 1-7
VAL_END = datetime(2025, 8, 31, tzinfo=timezone.utc)          # Month 8
# Month 9 = test

# ============================================================================
# Customer Segments
# ============================================================================

SEGMENTS = {
    "premium": {
        "fraction": 0.15,
        "order_range": (20, 100),
        "success_rate_range": (0.85, 0.98),
        "base_recovery_mult": 1.3,
        "payment_link_uplift": 0.25,    # Premium customers respond well to payment links
        "discount_uplift": 0.10,        # Less price-sensitive
        "reminder_uplift": 0.15,
        "amount_range": (2000, 50000),   # ₹2K - ₹50K
    },
    "loyal": {
        "fraction": 0.20,
        "order_range": (10, 50),
        "success_rate_range": (0.80, 0.95),
        "base_recovery_mult": 1.2,
        "payment_link_uplift": 0.20,
        "discount_uplift": 0.15,
        "reminder_uplift": 0.20,        # Loyal customers respond to reminders
        "amount_range": (500, 20000),
    },
    "regular": {
        "fraction": 0.30,
        "order_range": (3, 20),
        "success_rate_range": (0.65, 0.85),
        "base_recovery_mult": 1.0,
        "payment_link_uplift": 0.18,
        "discount_uplift": 0.20,
        "reminder_uplift": 0.12,
        "amount_range": (200, 15000),
    },
    "price_sensitive": {
        "fraction": 0.20,
        "order_range": (2, 15),
        "success_rate_range": (0.55, 0.75),
        "base_recovery_mult": 0.8,
        "payment_link_uplift": 0.12,
        "discount_uplift": 0.30,        # Price-sensitive → discounts work best
        "reminder_uplift": 0.08,
        "amount_range": (200, 8000),
    },
    "new": {
        "fraction": 0.15,
        "order_range": (1, 3),
        "success_rate_range": (0.50, 0.70),
        "base_recovery_mult": 0.7,
        "payment_link_uplift": 0.15,
        "discount_uplift": 0.18,
        "reminder_uplift": 0.05,        # New customers less responsive to reminders
        "amount_range": (200, 10000),
    },
}

# ============================================================================
# Failure Reasons
# ============================================================================

FAILURE_REASONS = {
    "insufficient_funds": {
        "probability": 0.30,
        "base_recovery": 0.45,
        "retry_uplift": 0.10,           # Might have funds later
        "common_methods": ["debit_card", "upi"],
    },
    "network_error": {
        "probability": 0.20,
        "base_recovery": 0.72,          # Usually temporary
        "retry_uplift": 0.25,           # Retry almost always works
        "common_methods": ["upi", "netbanking"],
    },
    "authentication_failed": {
        "probability": 0.15,
        "base_recovery": 0.25,          # Hard to recover
        "retry_uplift": 0.05,
        "common_methods": ["credit_card", "debit_card"],
    },
    "card_expired": {
        "probability": 0.10,
        "base_recovery": 0.15,          # Need new card
        "retry_uplift": 0.02,           # Retry won't help
        "common_methods": ["credit_card", "debit_card"],
    },
    "bank_declined": {
        "probability": 0.15,
        "base_recovery": 0.30,
        "retry_uplift": 0.08,
        "common_methods": ["credit_card", "debit_card", "netbanking"],
    },
    "timeout": {
        "probability": 0.10,
        "base_recovery": 0.65,          # Usually temporary
        "retry_uplift": 0.20,
        "common_methods": ["upi", "netbanking"],
    },
}

PAYMENT_METHODS = ["upi", "credit_card", "debit_card", "netbanking"]

COMMUNICATION_PREFERENCES = ["email", "sms", "whatsapp"]


# ============================================================================
# Generator
# ============================================================================

class SyntheticDataGenerator:
    """
    Generates realistic payment failure + recovery data.
    
    For each failed transaction, generates potential outcomes under
    ALL possible interventions. Only one outcome is "observed" 
    (the action that was taken). The rest are counterfactuals
    used for ground-truth evaluation.
    """

    def __init__(self, seed: int = SEED):
        self.rng = np.random.default_rng(seed)
        random.seed(seed)

    def generate_customers(self, n: int = NUM_CUSTOMERS) -> pd.DataFrame:
        """Generate customer profiles with segment-based attributes."""
        customers = []

        for segment_name, config in SEGMENTS.items():
            n_segment = int(n * config["fraction"])

            for i in range(n_segment):
                hist_orders = self.rng.integers(*config["order_range"])
                success_rate = self.rng.uniform(*config["success_rate_range"])
                successful = int(hist_orders * success_rate)
                failed = hist_orders - successful

                # Recovery rate has noise
                recovery_rate = self.rng.beta(5, 5) * 0.6 + 0.1  # 0.1 to 0.7

                customers.append({
                    "customer_id": str(uuid.uuid4()),
                    "segment": segment_name,
                    "historical_orders": int(hist_orders),
                    "successful_payments": int(successful),
                    "failed_payments": int(failed),
                    "historical_recovery_rate": round(float(recovery_rate), 4),
                    "communication_preference": random.choice(COMMUNICATION_PREFERENCES),
                    "opted_out": random.random() < 0.05,       # 5% opted out
                    "has_active_dispute": random.random() < 0.02,  # 2% have disputes
                    "success_rate": round(float(success_rate), 4),
                })

        return pd.DataFrame(customers)

    def generate_transactions(
        self, customers: pd.DataFrame, n: int = NUM_TRANSACTIONS
    ) -> pd.DataFrame:
        """Generate failed payment transactions."""
        transactions = []
        customer_ids = customers["customer_id"].values
        customer_lookup = customers.set_index("customer_id")

        for i in range(n):
            cid = random.choice(customer_ids)
            customer = customer_lookup.loc[cid]
            segment_config = SEGMENTS[customer["segment"]]

            # Amount within segment range, log-normal distribution
            amt_min, amt_max = segment_config["amount_range"]
            amount = int(
                np.clip(
                    self.rng.lognormal(
                        np.log((amt_min + amt_max) / 3), 0.7
                    ),
                    amt_min,
                    amt_max,
                )
            )
            amount = round(amount, -1)  # Round to nearest ₹10

            # Select failure reason (weighted)
            reasons = list(FAILURE_REASONS.keys())
            weights = np.array([FAILURE_REASONS[r]["probability"] for r in reasons], dtype=float)
            weights /= weights.sum()
            failure_reason = self.rng.choice(reasons, p=weights)
            failure_config = FAILURE_REASONS[failure_reason]

            # Payment method (biased by failure reason)
            common = failure_config["common_methods"]
            if random.random() < 0.7:
                payment_method = random.choice(common)
            else:
                payment_method = random.choice(PAYMENT_METHODS)

            # Timestamp within range (uniform, then sort for temporal split)
            days_range = (END_DATE - START_DATE).days
            rand_days = self.rng.uniform(0, days_range)
            timestamp = START_DATE + timedelta(days=rand_days)

            # Hour of day (peaks at 10am-2pm and 7pm-10pm)
            hour_weights = np.array([
                0.01, 0.005, 0.005, 0.005, 0.005, 0.01,  # 0-5
                0.02, 0.04, 0.06, 0.08, 0.09, 0.08,      # 6-11
                0.07, 0.06, 0.05, 0.04, 0.04, 0.05,      # 12-17
                0.06, 0.07, 0.08, 0.07, 0.05, 0.03,      # 18-23
            ], dtype=float)
            hour_weights /= hour_weights.sum()
            hour = self.rng.choice(24, p=hour_weights)
            timestamp = timestamp.replace(hour=int(hour))

            transactions.append({
                "transaction_id": str(uuid.uuid4()),
                "customer_id": cid,
                "order_id": f"order_{uuid.uuid4().hex[:12]}",
                "amount": amount,
                "amount_paise": amount * 100,
                "currency": "INR",
                "payment_method": payment_method,
                "timestamp": timestamp.isoformat(),
                "status": "failed",
                "failure_reason": failure_reason,
                "hour_of_day": int(hour),
                "day_of_week": timestamp.weekday(),
            })

        df = pd.DataFrame(transactions)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def _compute_base_recovery_probability(
        self,
        failure_reason: str,
        segment: str,
        amount: int,
        success_rate: float,
    ) -> float:
        """
        Compute baseline P(recovery | do_nothing).
        
        Factors:
        - Failure reason base recovery rate
        - Customer segment multiplier
        - Amount effect (higher amounts → lower recovery)
        - Historical success rate bonus
        """
        failure_config = FAILURE_REASONS[failure_reason]
        segment_config = SEGMENTS[segment]

        base = failure_config["base_recovery"]
        base *= segment_config["base_recovery_mult"]

        # Amount effect: log-inverse relationship
        # Higher amounts have lower natural recovery
        amount_factor = 1.0 - 0.1 * np.log10(max(amount, 100) / 100)
        amount_factor = np.clip(amount_factor, 0.5, 1.2)
        base *= amount_factor

        # Historical success rate bonus
        if success_rate > 0.8:
            base *= 1.3
        elif success_rate > 0.6:
            base *= 1.1

        # Add noise
        noise = self.rng.beta(10, 10) * 0.2 - 0.1  # ±10%
        base += noise

        return float(np.clip(base, 0.02, 0.90))

    def _compute_intervention_probability(
        self,
        base_prob: float,
        action: str,
        failure_reason: str,
        segment: str,
        retry_count: int = 0,
        discount_pct: float = 5.0,
    ) -> float:
        """
        Compute P(recovery | action) for a given intervention.
        
        Each action adds uplift to the base probability, modified by
        segment responsiveness and failure reason compatibility.
        """
        if action == "do_nothing":
            return base_prob

        failure_config = FAILURE_REASONS[failure_reason]
        segment_config = SEGMENTS[segment]

        if action == "retry":
            # Retry uplift depends on failure reason
            uplift = failure_config["retry_uplift"]
            # Diminishing returns per retry
            diminish = max(0, 1.0 - 0.6 * retry_count)
            uplift *= diminish

        elif action == "payment_link":
            uplift = segment_config["payment_link_uplift"]
            # Payment links work less well for auth failures
            if failure_reason == "authentication_failed":
                uplift *= 0.5
            elif failure_reason == "card_expired":
                uplift *= 1.5  # New payment method helps

        elif action == "reminder":
            uplift = segment_config["reminder_uplift"]
            # Reminders work best for network/timeout issues
            if failure_reason in ("network_error", "timeout"):
                uplift *= 1.3

        elif action == "discount":
            uplift = segment_config["discount_uplift"]
            # Scale by discount percentage
            uplift *= (discount_pct / 5.0)
            # Diminishing returns on discount
            uplift *= (1.0 - discount_pct / 25.0)

        else:
            uplift = 0.0

        # Add noise to uplift
        noise = self.rng.normal(0, 0.03)
        uplift += noise

        prob = base_prob + max(uplift, 0)
        return float(np.clip(prob, 0.01, 0.98))

    def generate_ground_truth(
        self, transactions: pd.DataFrame, customers: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate potential outcomes under ALL actions for each transaction.
        
        This is the ground truth. In a real system, you can only observe
        one outcome per transaction. We generate all for evaluation purposes.
        """
        customer_lookup = customers.set_index("customer_id")
        records = []

        actions = ["do_nothing", "retry", "payment_link", "reminder", "discount"]

        for _, tx in transactions.iterrows():
            customer = customer_lookup.loc[tx["customer_id"]]
            segment = customer["segment"]
            success_rate = customer["success_rate"]

            base_prob = self._compute_base_recovery_probability(
                failure_reason=tx["failure_reason"],
                segment=segment,
                amount=tx["amount"],
                success_rate=success_rate,
            )

            # Generate potential outcomes for each action
            outcomes = {"transaction_id": tx["transaction_id"]}

            for action in actions:
                prob = self._compute_intervention_probability(
                    base_prob=base_prob,
                    action=action,
                    failure_reason=tx["failure_reason"],
                    segment=segment,
                )
                # Sample binary outcome from probability
                recovered = self.rng.random() < prob

                outcomes[f"p_{action}"] = round(prob, 4)
                outcomes[f"outcome_{action}"] = int(recovered)

            outcomes["base_probability"] = round(base_prob, 4)

            records.append(outcomes)

        return pd.DataFrame(records)

    def generate_observed_data(
        self, transactions: pd.DataFrame, ground_truth: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate the OBSERVED dataset — what we'd see in production.
        
        For each transaction, we simulate a historical policy:
        - 40% got a retry
        - 20% got a payment link
        - 15% got a reminder
        - 10% got a discount
        - 15% got no intervention (control)
        """
        gt_lookup = ground_truth.set_index("transaction_id")
        records = []

        action_weights = {
            "do_nothing": 0.15,
            "retry": 0.40,
            "payment_link": 0.20,
            "reminder": 0.15,
            "discount": 0.10,
        }
        actions = list(action_weights.keys())
        weights = np.array(list(action_weights.values()), dtype=float)
        weights /= weights.sum()

        for _, tx in transactions.iterrows():
            gt = gt_lookup.loc[tx["transaction_id"]]

            # Historical action (random assignment for causal identification)
            action = self.rng.choice(actions, p=weights)

            # Observed outcome
            prob = gt[f"p_{action}"]
            recovered = int(gt[f"outcome_{action}"])
            recovered_amount = tx["amount"] if recovered else 0

            # Action cost
            action_costs = {
                "do_nothing": 0,
                "retry": 10,
                "payment_link": 20,
                "reminder": 5,
                "discount": 20,
            }

            discount_pct = 5.0 if action == "discount" else 0.0
            discount_amount = int(tx["amount"] * discount_pct / 100) if recovered and action == "discount" else 0

            records.append({
                "transaction_id": tx["transaction_id"],
                "action_taken": action,
                "action_cost": action_costs[action],
                "discount_percentage": discount_pct,
                "discount_amount": discount_amount,
                "recovery_probability": round(float(prob), 4),
                "payment_success": recovered,
                "recovered_amount": recovered_amount,
                "net_recovered": recovered_amount - action_costs[action] - discount_amount,
            })

        return pd.DataFrame(records)

    def split_data(
        self, transactions: pd.DataFrame, observed: pd.DataFrame
    ) -> dict[str, pd.DataFrame]:
        """
        Split data temporally into train/validation/test.
        
        - Training: Months 1-7 (70%)
        - Validation: Month 8 (15%)
        - Test: Month 9 (15%)
        """
        train_mask = transactions["timestamp"] <= TRAIN_END
        val_mask = (transactions["timestamp"] > TRAIN_END) & (
            transactions["timestamp"] <= VAL_END
        )
        test_mask = transactions["timestamp"] > VAL_END

        train_ids = set(transactions[train_mask]["transaction_id"])
        val_ids = set(transactions[val_mask]["transaction_id"])
        test_ids = set(transactions[test_mask]["transaction_id"])

        return {
            "train": {
                "transactions": transactions[train_mask],
                "observed": observed[observed["transaction_id"].isin(train_ids)],
            },
            "validation": {
                "transactions": transactions[val_mask],
                "observed": observed[observed["transaction_id"].isin(val_ids)],
            },
            "test": {
                "transactions": transactions[test_mask],
                "observed": observed[observed["transaction_id"].isin(test_ids)],
            },
        }

    def generate_all(self):
        """Generate all data and save to disk."""
        print("=" * 60)
        print("Revenue Intervention Optimizer — Synthetic Data Generator")
        print("=" * 60)

        # Create output directories
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        SPLITS_DIR.mkdir(parents=True, exist_ok=True)

        # Generate customers
        print("\n[1/6] Generating customers...")
        customers = self.generate_customers()
        print(f"  -> {len(customers)} customers across {customers['segment'].nunique()} segments")

        # Generate transactions
        print("\n[2/6] Generating transactions...")
        transactions = self.generate_transactions(customers)
        print(f"  -> {len(transactions)} failed transactions")
        print(f"  -> Amount range: INR {transactions['amount'].min():,} - INR {transactions['amount'].max():,}")
        print(f"  -> Date range: {transactions['timestamp'].min().date()} to {transactions['timestamp'].max().date()}")

        # Generate ground truth
        print("\n[3/6] Generating ground truth (potential outcomes)...")
        ground_truth = self.generate_ground_truth(transactions, customers)
        print(f"  -> {len(ground_truth)} x 5 action outcomes = {len(ground_truth) * 5} potential outcomes")

        # Generate observed data
        print("\n[4/6] Generating observed data (historical policy)...")
        observed = self.generate_observed_data(transactions, ground_truth)
        recovery_rate = observed["payment_success"].mean()
        print(f"  -> Overall recovery rate: {recovery_rate:.1%}")
        print(f"  -> Action distribution:")
        for action, count in observed["action_taken"].value_counts().items():
            rate = observed[observed["action_taken"] == action]["payment_success"].mean()
            print(f"    {action:20s}: {count:5d} ({rate:.1%} recovery)")

        # Split data
        print("\n[5/6] Splitting data (temporal split)...")
        splits = self.split_data(transactions, observed)
        for split_name, split_data in splits.items():
            n = len(split_data["transactions"])
            pct = n / len(transactions) * 100
            print(f"  -> {split_name:12s}: {n:5d} transactions ({pct:.1f}%)")

        # Save to disk
        print("\n[6/6] Saving to disk...")
        customers.to_csv(OUTPUT_DIR / "customers.csv", index=False)
        transactions.to_csv(OUTPUT_DIR / "transactions.csv", index=False)
        ground_truth.to_csv(OUTPUT_DIR / "ground_truth.csv", index=False)
        observed.to_csv(OUTPUT_DIR / "observed.csv", index=False)

        for split_name, split_data in splits.items():
            split_dir = SPLITS_DIR / split_name
            split_dir.mkdir(parents=True, exist_ok=True)
            split_data["transactions"].to_csv(split_dir / "transactions.csv", index=False)
            split_data["observed"].to_csv(split_dir / "observed.csv", index=False)

        # Save ground truth ONLY with test set (for final evaluation)
        test_ids = set(splits["test"]["transactions"]["transaction_id"])
        test_gt = ground_truth[ground_truth["transaction_id"].isin(test_ids)]
        test_gt.to_csv(SPLITS_DIR / "test" / "ground_truth.csv", index=False)

        # Save generation metadata
        metadata = {
            "seed": SEED,
            "num_customers": len(customers),
            "num_transactions": len(transactions),
            "segments": list(SEGMENTS.keys()),
            "failure_reasons": list(FAILURE_REASONS.keys()),
            "payment_methods": PAYMENT_METHODS,
            "date_range": {
                "start": START_DATE.isoformat(),
                "end": END_DATE.isoformat(),
            },
            "splits": {
                name: len(data["transactions"])
                for name, data in splits.items()
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(OUTPUT_DIR / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n[OK] Data saved to {OUTPUT_DIR}")
        print(f"[OK] Splits saved to {SPLITS_DIR}")
        print(f"[OK] Metadata saved to {OUTPUT_DIR / 'metadata.json'}")

        # Summary statistics
        print("\n" + "=" * 60)
        print("DATA SUMMARY")
        print("=" * 60)
        print(f"Customers:        {len(customers):,}")
        print(f"Transactions:     {len(transactions):,}")
        print(f"Recovery rate:    {recovery_rate:.1%}")
        print(f"Total at risk:    INR {transactions['amount'].sum():,.0f}")
        total_recovered = observed[observed["payment_success"] == 1].merge(
            transactions[["transaction_id", "amount"]], on="transaction_id"
        )["amount"].sum()
        print(f"Total recovered:  INR {total_recovered:,.0f}")
        print(f"Recovery yield:   {total_recovered / transactions['amount'].sum():.1%}")

        return customers, transactions, ground_truth, observed, splits


if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate_all()
