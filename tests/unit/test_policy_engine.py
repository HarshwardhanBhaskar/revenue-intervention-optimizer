"""
Unit tests for the Policy Engine.

Tests every policy rule, edge cases, and combinations.
The policy engine is the most critical safety component —
it must be thoroughly tested.
"""

import pytest
from datetime import datetime, timezone, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from domain.policy_engine import (
    PolicyEngine,
    PolicyConfig,
    RecoveryContext,
    RecommendedAction,
    PolicyCheck,
    PolicyResult,
)
from events.event_types import ActionType, PolicyStatus


@pytest.fixture
def default_policy():
    return PolicyConfig()


@pytest.fixture
def engine(default_policy):
    return PolicyEngine(default_policy)


@pytest.fixture
def basic_context():
    return RecoveryContext(amount_paise=500_000)  # ₹5,000


@pytest.fixture
def high_value_context():
    return RecoveryContext(amount_paise=2_000_000)  # ₹20,000


class TestDoNothing:
    """DO_NOTHING should always be approved."""

    def test_do_nothing_always_approved(self, engine, basic_context):
        action = RecommendedAction(action_type=ActionType.DO_NOTHING)
        result = engine.evaluate(action, basic_context)
        assert result.status == PolicyStatus.APPROVED
        assert result.is_approved

    def test_do_nothing_even_with_dispute(self, engine):
        context = RecoveryContext(amount_paise=500_000, customer_has_dispute=True)
        action = RecommendedAction(action_type=ActionType.DO_NOTHING)
        result = engine.evaluate(action, context)
        assert result.is_approved

    def test_do_nothing_even_with_opt_out(self, engine):
        context = RecoveryContext(amount_paise=500_000, customer_opted_out=True)
        action = RecommendedAction(action_type=ActionType.DO_NOTHING)
        result = engine.evaluate(action, context)
        assert result.is_approved


class TestHumanReview:
    """HUMAN_REVIEW should always require human approval."""

    def test_human_review_requires_human(self, engine, basic_context):
        action = RecommendedAction(action_type=ActionType.HUMAN_REVIEW)
        result = engine.evaluate(action, basic_context)
        assert result.status == PolicyStatus.REQUIRES_HUMAN
        assert result.requires_human


class TestCustomerOptOut:
    """Opted-out customers must not receive communications."""

    def test_reminder_blocked_when_opted_out(self, engine):
        context = RecoveryContext(amount_paise=500_000, customer_opted_out=True)
        action = RecommendedAction(
            action_type=ActionType.REMINDER,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked
        assert "customer_opt_out" in result.blocking_rules

    def test_payment_link_blocked_when_opted_out(self, engine):
        context = RecoveryContext(amount_paise=500_000, customer_opted_out=True)
        action = RecommendedAction(
            action_type=ActionType.PAYMENT_LINK,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked

    def test_retry_allowed_when_opted_out(self, engine):
        """Retry doesn't involve customer communication."""
        context = RecoveryContext(amount_paise=500_000, customer_opted_out=True)
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_approved

    def test_opt_out_not_enforced_when_disabled(self):
        config = PolicyConfig(enforce_opt_out=False)
        engine = PolicyEngine(config)
        context = RecoveryContext(amount_paise=500_000, customer_opted_out=True)
        action = RecommendedAction(
            action_type=ActionType.REMINDER,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_approved


class TestActiveDispute:
    """Active disputes must block all recovery actions."""

    def test_retry_blocked_with_dispute(self, engine):
        context = RecoveryContext(amount_paise=500_000, customer_has_dispute=True)
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked
        assert "active_dispute" in result.blocking_rules

    def test_dispute_not_enforced_when_disabled(self):
        config = PolicyConfig(block_disputed=False)
        engine = PolicyEngine(config)
        context = RecoveryContext(amount_paise=500_000, customer_has_dispute=True)
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_approved


class TestRetryLimits:
    """Retry count must be enforced."""

    def test_first_retry_allowed(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved

    def test_retry_at_limit_blocked(self, engine):
        context = RecoveryContext(amount_paise=500_000, retry_count=2)
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked
        assert "max_retry_attempts" in result.blocking_rules

    def test_retry_above_limit_blocked(self, engine):
        context = RecoveryContext(amount_paise=500_000, retry_count=5)
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked


class TestDiscountCap:
    """Discount percentage must respect cap."""

    def test_discount_within_cap(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.DISCOUNT,
            discount_percentage=5.0,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved

    def test_discount_above_cap_blocked(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.DISCOUNT,
            discount_percentage=10.0,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_blocked
        assert "max_discount" in result.blocking_rules


class TestMinIncrementalValue:
    """Actions below minimum incremental value should be blocked."""

    def test_above_threshold_approved(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,  # ₹500 > ₹100 threshold
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved

    def test_below_threshold_blocked(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=5_000,  # ₹50 < ₹100 threshold
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_blocked
        assert "min_incremental_value" in result.blocking_rules

    def test_exactly_at_threshold_approved(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=10_000,  # ₹100 = threshold
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved


class TestHumanApprovalThreshold:
    """High-value transactions require human approval."""

    def test_below_threshold_auto_approved(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved

    def test_above_threshold_requires_human(self, engine, high_value_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=200_000,
        )
        result = engine.evaluate(action, high_value_context)
        assert result.requires_human


class TestContactInterval:
    """Minimum contact interval must be enforced."""

    def test_no_previous_contact_allowed(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.REMINDER,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        assert result.is_approved

    def test_recent_contact_blocked(self, engine):
        context = RecoveryContext(
            amount_paise=500_000,
            last_contact_at=datetime.now(timezone.utc) - timedelta(hours=6),
        )
        action = RecommendedAction(
            action_type=ActionType.REMINDER,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked
        assert "min_contact_interval" in result.blocking_rules

    def test_old_contact_allowed(self, engine):
        context = RecoveryContext(
            amount_paise=500_000,
            last_contact_at=datetime.now(timezone.utc) - timedelta(hours=48),
        )
        action = RecommendedAction(
            action_type=ActionType.REMINDER,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, context)
        assert result.is_approved


class TestMultipleViolations:
    """Multiple policy violations should all be reported."""

    def test_multiple_violations(self, engine):
        context = RecoveryContext(
            amount_paise=500_000,
            customer_opted_out=True,
            customer_has_dispute=True,
        )
        action = RecommendedAction(
            action_type=ActionType.PAYMENT_LINK,
            expected_incremental_value_paise=5_000,  # Below threshold too
        )
        result = engine.evaluate(action, context)
        assert result.is_blocked
        assert len(result.blocking_rules) >= 2


class TestPolicyResultSerialization:
    """PolicyResult should serialize correctly."""

    def test_to_dict(self, engine, basic_context):
        action = RecommendedAction(
            action_type=ActionType.RETRY,
            expected_incremental_value_paise=50_000,
        )
        result = engine.evaluate(action, basic_context)
        d = result.to_dict()
        assert "status" in d
        assert "checks" in d
        assert isinstance(d["checks"], list)
