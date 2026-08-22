"""
Baseline Model & Rule-Based Recovery Policy.

Implements standard industry heuristics (e.g. "retry once for every failure")
as the benchmark against which the AI uplift model is compared.
"""

import pandas as pd
from events.event_types import ActionType


class BaselinePolicy:
    """Standard rule-based recovery policy."""

    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries

    def decide(self, transaction_row: dict | pd.Series) -> ActionType:
        """
        Decide action using rule-based heuristic:
        Retry once; then do nothing.
        """
        retry_count = transaction_row.get("retry_count", 0)
        if retry_count < self.max_retries:
            return ActionType.RETRY
        return ActionType.DO_NOTHING
