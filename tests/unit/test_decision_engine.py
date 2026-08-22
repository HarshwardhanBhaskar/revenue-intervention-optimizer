"""
Unit tests for the Decision Engine.

Tests economic calculations, action ranking, and the
incremental value computation.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from domain.decision_engine import (
    DecisionEngine,
    ActionEconomics,
    ActionRanking,
    DEFAULT_ACTION_COSTS,
)
from events.event_types import ActionType


@pytest.fixture
def engine():
    return DecisionEngine()


class TestActionEconomics:
    """Test individual action economic calculations."""

    def test_do_nothing_has_zero_cost(self, engine):
        result = engine.compute_action_economics(
            action_type=ActionType.DO_NOTHING,
            amount_paise=749_900,  # ₹7,499
            p_recovery=0.31,
            p_baseline=0.31,
        )
        assert result.action_cost_paise == 0
        assert result.discount_cost_paise == 0
        assert result.incremental_value_paise == 0

    def test_retry_economics(self, engine):
        """
        Order value: ₹7,499
        P(retry) = 54%, P(baseline) = 31%
        Retry cost: ₹10
        Expected value: 0.54 × 74990 - 1000 = 40494.6 - 1000 ≈ 39495
        Baseline: 0.31 × 74990 ≈ 23246
        Incremental: 39495 - 23246 = 16249 (≈ ₹162)
        """
        result = engine.compute_action_economics(
            action_type=ActionType.RETRY,
            amount_paise=749_900,
            p_recovery=0.54,
            p_baseline=0.31,
        )
        assert result.action_cost_paise == 1_000  # ₹10
        assert result.expected_revenue_paise == int(0.54 * 749_900)
        assert result.incremental_value_paise > 0
        assert result.discount_cost_paise == 0

    def test_discount_economics_include_discount_cost(self, engine):
        """Discount cost is only paid when recovery succeeds."""
        result = engine.compute_action_economics(
            action_type=ActionType.DISCOUNT,
            amount_paise=749_900,
            p_recovery=0.76,
            p_baseline=0.31,
            discount_pct=5.0,
        )
        assert result.discount_percentage == 5.0
        # Discount cost = P(recovery) × amount × discount%
        expected_discount = int(0.76 * 749_900 * 0.05)
        assert result.discount_cost_paise == expected_discount
        assert result.action_cost_paise > 0

    def test_negative_incremental_when_cost_exceeds_uplift(self, engine):
        """When intervention cost > uplift, incremental value should be negative."""
        result = engine.compute_action_economics(
            action_type=ActionType.RETRY,
            amount_paise=100_00,  # ₹100 — small transaction
            p_recovery=0.32,     # Barely above baseline
            p_baseline=0.31,
        )
        # Small amount + small uplift = likely negative after cost
        # Whether this is positive or negative depends on exact numbers
        # The point is the calculation is correct
        expected_revenue = int(0.32 * 100_00)
        baseline_expected = int(0.31 * 100_00)
        expected_net = expected_revenue - 1_000  # ₹10 cost
        expected_incremental = expected_net - baseline_expected
        assert result.incremental_value_paise == expected_incremental

    def test_zero_probability_zero_value(self, engine):
        result = engine.compute_action_economics(
            action_type=ActionType.RETRY,
            amount_paise=500_000,
            p_recovery=0.0,
            p_baseline=0.0,
        )
        assert result.expected_revenue_paise == 0
        assert result.incremental_value_paise == -1_000  # Just the cost


class TestActionRanking:
    """Test action ranking and recommendation logic."""

    def test_ranks_by_incremental_value(self, engine):
        predictions = {
            ActionType.DO_NOTHING: 0.31,
            ActionType.RETRY: 0.54,
            ActionType.PAYMENT_LINK: 0.71,
            ActionType.REMINDER: 0.40,
            ActionType.DISCOUNT: 0.76,
        }
        ranking = engine.evaluate_actions(
            amount_paise=749_900,
            predictions=predictions,
        )
        # Should be sorted by incremental value descending
        for i in range(len(ranking.rankings) - 1):
            assert (
                ranking.rankings[i].incremental_value_paise
                >= ranking.rankings[i + 1].incremental_value_paise
            )

    def test_recommends_best_action(self, engine):
        predictions = {
            ActionType.DO_NOTHING: 0.31,
            ActionType.RETRY: 0.54,
            ActionType.PAYMENT_LINK: 0.71,
        }
        ranking = engine.evaluate_actions(
            amount_paise=749_900,
            predictions=predictions,
        )
        assert ranking.recommended_action is not None
        assert ranking.recommended_incremental_value_paise > 0

    def test_recommends_do_nothing_when_below_threshold(self, engine):
        """When no action exceeds threshold, recommend DO_NOTHING."""
        predictions = {
            ActionType.DO_NOTHING: 0.50,
            ActionType.RETRY: 0.51,      # Tiny uplift
        }
        ranking = engine.evaluate_actions(
            amount_paise=100_00,          # Small amount
            predictions=predictions,
            min_incremental_value_paise=100_000,  # ₹1000 threshold — high
        )
        assert ranking.recommended_action == ActionType.DO_NOTHING

    def test_all_actions_present_in_ranking(self, engine):
        predictions = {
            ActionType.DO_NOTHING: 0.31,
            ActionType.RETRY: 0.54,
            ActionType.PAYMENT_LINK: 0.71,
            ActionType.REMINDER: 0.40,
            ActionType.DISCOUNT: 0.76,
        }
        ranking = engine.evaluate_actions(
            amount_paise=749_900,
            predictions=predictions,
        )
        action_types_in_ranking = {r.action_type for r in ranking.rankings}
        assert action_types_in_ranking == set(predictions.keys())

    def test_ranking_serialization(self, engine):
        predictions = {
            ActionType.DO_NOTHING: 0.31,
            ActionType.RETRY: 0.54,
        }
        ranking = engine.evaluate_actions(
            amount_paise=749_900,
            predictions=predictions,
        )
        d = ranking.to_dict()
        assert "recommended_action" in d
        assert "rankings" in d
        assert len(d["rankings"]) == 2


class TestDiscountSimulation:
    """Test discount scenario simulation for Decision Lab."""

    def test_multiple_discount_scenarios(self, engine):
        scenarios = engine.simulate_discount_scenarios(
            amount_paise=749_900,
            p_baseline=0.31,
            p_discount_base=0.70,
            discount_percentages=[2.0, 5.0, 8.0, 10.0],
        )
        assert len(scenarios) == 4
        # All should have discount_percentage > 0
        for s in scenarios:
            assert s.discount_percentage > 0
            assert s.discount_cost_paise > 0

    def test_higher_discount_higher_probability(self, engine):
        """Higher discount should generally give higher probability."""
        scenarios = engine.simulate_discount_scenarios(
            amount_paise=749_900,
            p_baseline=0.31,
            p_discount_base=0.50,
            discount_percentages=[2.0, 10.0],
        )
        assert scenarios[1].probability >= scenarios[0].probability


class TestEdgeCases:
    """Test edge cases in economic calculations."""

    def test_very_small_amount(self, engine):
        result = engine.compute_action_economics(
            action_type=ActionType.RETRY,
            amount_paise=100,  # ₹1
            p_recovery=0.50,
            p_baseline=0.30,
        )
        # Should not crash
        assert isinstance(result.incremental_value_paise, int)

    def test_very_large_amount(self, engine):
        result = engine.compute_action_economics(
            action_type=ActionType.PAYMENT_LINK,
            amount_paise=5_000_000_00,  # ₹50,00,000
            p_recovery=0.80,
            p_baseline=0.20,
        )
        assert result.incremental_value_paise > 0

    def test_probability_at_boundaries(self, engine):
        for p in [0.0, 0.5, 1.0]:
            result = engine.compute_action_economics(
                action_type=ActionType.RETRY,
                amount_paise=100_000,
                p_recovery=p,
                p_baseline=0.3,
            )
            assert isinstance(result.incremental_value_paise, int)
