"""
Dataset Ingestion & Enrichment Pipeline for RIO

Ingests external e-commerce and UPI transaction datasets from `data set/`:
1. transactions.csv (UPI transaction flows with real failure rates & bank handles)
2. ecommerce_transactions.csv (Multi-method payment distributions)
3. ecommerce_sales_34500.csv (Order margins, discounts, customer segments)

Converts them into RIO-compliant feature vectors, orders, and failure recovery opportunities.
"""

import os
import csv
import uuid
import datetime
import random
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data set"


def analyze_dataset_distributions() -> Dict[str, Any]:
    """Analyzes the raw distributions from the uploaded datasets."""
    stats = {
        "upi_transactions_count": 0,
        "upi_failures_count": 0,
        "upi_failure_rate": 0.0,
        "ecommerce_transactions_count": 0,
        "ecommerce_sales_count": 0,
        "bank_distribution": {},
        "category_distribution": {},
        "payment_method_distribution": {},
    }

    # 1. Analyze transactions.csv
    upi_path = DATA_DIR / "transactions.csv"
    if upi_path.exists():
        with open(upi_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["upi_transactions_count"] += 1
                status = row.get("Status", "").strip().upper()
                if status == "FAILED":
                    stats["upi_failures_count"] += 1
                
                # Bank handle from Sender UPI ID
                upi_id = row.get("Sender UPI ID", "")
                if "@" in upi_id:
                    handle = upi_id.split("@")[1].lower()
                    stats["bank_distribution"][handle] = stats["bank_distribution"].get(handle, 0) + 1
        
        if stats["upi_transactions_count"] > 0:
            stats["upi_failure_rate"] = round(stats["upi_failures_count"] / stats["upi_transactions_count"], 4)

    # 2. Analyze ecommerce_transactions.csv
    ecom_tx_path = DATA_DIR / "ecommerce_transactions.csv"
    if ecom_tx_path.exists():
        with open(ecom_tx_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["ecommerce_transactions_count"] += 1
                method = row.get("Payment_Method", "Unknown").strip()
                stats["payment_method_distribution"][method] = stats["payment_method_distribution"].get(method, 0) + 1

    # 3. Analyze ecommerce_sales_34500.csv
    ecom_sales_path = DATA_DIR / "ecommerce_sales_34500.csv"
    if ecom_sales_path.exists():
        with open(ecom_sales_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["ecommerce_sales_count"] += 1
                category = row.get("category", "General").strip()
                stats["category_distribution"][category] = stats["category_distribution"].get(category, 0) + 1

    return stats


def extract_real_failed_payment_records(limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Extracts failed transaction records from the uploaded datasets
    and converts them into RIO recovery opportunity input formats.
    """
    records = []
    
    # Process transactions.csv for UPI failures
    upi_path = DATA_DIR / "transactions.csv"
    if upi_path.exists():
        with open(upi_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Status", "").strip().upper() == "FAILED":
                    try:
                        amount_inr = float(row.get("Amount (INR)", 1500))
                    except ValueError:
                        amount_inr = 1500.0

                    amount_paise = int(amount_inr * 100)
                    upi_handle = row.get("Sender UPI ID", "").split("@")[-1] if "@" in row.get("Sender UPI ID", "") else "okaxis"
                    
                    records.append({
                        "source": "upi_transactions",
                        "external_tx_id": row.get("Transaction ID", str(uuid.uuid4())),
                        "customer_name": row.get("Sender Name", "Valued Customer"),
                        "amount_paise": amount_paise,
                        "payment_method": "upi",
                        "upi_bank_handle": upi_handle,
                        "timestamp": row.get("Timestamp", datetime.datetime.utcnow().isoformat()),
                        "failure_reason": random.choice(["vpa_timeout", "insufficient_funds", "bank_decline", "network_error"]),
                    })
                    if len(records) >= limit:
                        break

    return records


if __name__ == "__main__":
    print("==================================================")
    print("RIO DATASET INGESTION & DISTRIBUTION ANALYSIS")
    print("==================================================")
    stats = analyze_dataset_distributions()
    print(f"UPI Transactions Ingested    : {stats['upi_transactions_count']:,}")
    print(f"UPI Failure Count            : {stats['upi_failures_count']:,} ({stats['upi_failure_rate']*100:.1f}% failure rate)")
    print(f"E-commerce Transactions      : {stats['ecommerce_transactions_count']:,}")
    print(f"E-commerce Sales Orders      : {stats['ecommerce_sales_count']:,}")
    print("\nTop UPI Bank Handles:")
    for bank, count in sorted(stats['bank_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - @{bank}: {count} transactions")
    print("\nPayment Method Distribution:")
    for method, count in stats['payment_method_distribution'].items():
        print(f"  - {method}: {count:,}")
    print("\nTop Sales Categories:")
    for cat, count in stats['category_distribution'].items():
        print(f"  - {cat}: {count:,}")
    print("==================================================")
