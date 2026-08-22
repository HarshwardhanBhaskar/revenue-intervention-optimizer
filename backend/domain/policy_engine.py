"""
Policy Engine — Deterministic financial policy enforcement.

This is the most critical safety layer. All rules are deterministic,
testable, and enforced server-side. No ML or LLM involvement.

Policy rules:
1. max_automated_amount — Amount exceeding limit requires human approval
2. max_discount — Discount percentage cap
3. max_retry_attempts — Stop retrying after N attempts
4. min_incremental_value — DO_NOTHING if expected uplift is too low
5. customer_opt_out — Block communication if customer opted out
6. active_dispute — Block recovery if customer has active dispute
7. min_contact_interval — Minimum hours between contacts
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from events.event_types import ActionType, PolicyStatus


@dataclass
class PolicyCheck:
    """Result of a single policy rule evaluation."""
    rule: str
    passed: bool
    details: str


@dataclass
class PolicyResult:
    """Aggregate result of all policy checks."""
    status: PolicyStatus
    checks: list[PolicyCheck] = field(default_factory=list)
    blocking_rules: list[str] = field(default_factory=list)

    @property
    def is_approved(self) -> bool:
        return self.status == PolicyStatus.APPROVED

    @property
    def is_blocked(self) -> bool:
        return self.status == PolicyStatus.BLOCKED

    @property
    def requires_human(self) -> bool:
        return self.status == PolicyStatus.REQUIRES_HUMAN

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "checks": [
                {"rule": c.rule, "passed": c.passed, "details": c.details}
                for c in self.checks
            ],
            "blocking_rules": self.blocking_rules,
        }


@dataclass
class PolicyConfig:
    """Merchant policy configuration."""
    max_automated_amount_paise: int = 1_000_000     # ₹10,000
    max_discount_percentage: float = 5.0            # 5%
    max_retry_attempts: int = 2
    min_incremental_value_paise: int = 10_000       # ₹100
    human_approval_threshold_paise: int = 1_000_000 # ₹10,000
    min_contact_interval_hours: int = 24
    enforce_opt_out: bool = True
    block_disputed: bool = True
    block_fraud_signals: bool = True


@dataclass
class RecoveryContext:
    """Context for policy evaluation."""
    amount_paise: int
    customer_opted_out: bool = False
    customer_has_dispute: bool = False
    customer_has_fraud_signal: bool = False
    retry_count: int = 0
    last_contact_at: Optional[datetime] = None


@dataclass
class RecommendedAction:
    """An action recommended by the decision engine."""
    action_type: ActionType
    expected_incremental_value_paise: int = 0
    discount_percentage: float = 0.0
    action_cost_paise: int = 0


class PolicyEngine:
    """
    Deterministic policy engine. Evaluates all rules and returns
    APPROVED, BLOCKED, or REQUIRES_HUMAN.

    This engine NEVER uses ML or LLM. All decisions are based on
    explicit, testable rules configured by the merchant.
    """

    def __init__(self, config: PolicyConfig):
        self.config = config

    def evaluate(
        self,
        action: RecommendedAction,
        context: RecoveryContext,
    ) -> PolicyResult:
        """
        Evaluate all policy rules against the recommended action.

        Returns PolicyResult with status and detailed check results.
        """
        checks: list[PolicyCheck] = []
        blocking_rules: list[str] = []

        # Rule 1: DO_NOTHING always passes (it's always a valid choice)
        if action.action_type == ActionType.DO_NOTHING:
            checks.append(PolicyCheck(
                rule="do_nothing",
                passed=True,
                details="DO_NOTHING is always policy-compliant"
            ))
            return PolicyResult(
                status=PolicyStatus.APPROVED,
                checks=checks,
                blocking_rules=[],
            )

        # Rule 2: HUMAN_REVIEW always passes (it's an escalation)
        if action.action_type == ActionType.HUMAN_REVIEW:
            checks.append(PolicyCheck(
                rule="human_review",
                passed=True,
                details="HUMAN_REVIEW is always policy-compliant"
            ))
            return PolicyResult(
                status=PolicyStatus.REQUIRES_HUMAN,
                checks=checks,
                blocking_rules=[],
            )

        # Rule 3: Customer opt-out — blocks communication actions
        if self.config.enforce_opt_out and context.customer_opted_out:
            if action.action_type in (
                ActionType.REMINDER,
                ActionType.PAYMENT_LINK,
                ActionType.DISCOUNT,
            ):
                check = PolicyCheck(
                    rule="customer_opt_out",
                    passed=False,
                    details="Customer has opted out of communications"
                )
                checks.append(check)
                blocking_rules.append("customer_opt_out")

        # Rule 4: Active dispute — blocks all recovery actions
        if self.config.block_disputed and context.customer_has_dispute:
            check = PolicyCheck(
                rule="active_dispute",
                passed=False,
                details="Customer has an active dispute — recovery blocked"
            )
            checks.append(check)
            blocking_rules.append("active_dispute")

        # Rule 5: Fraud signals — blocks all recovery actions
        if self.config.block_fraud_signals and context.customer_has_fraud_signal:
            check = PolicyCheck(
                rule="fraud_signal",
                passed=False,
                details="Fraud signal detected — recovery blocked"
            )
            checks.append(check)
            blocking_rules.append("fraud_signal")

        # Rule 6: Retry limit
        if action.action_type == ActionType.RETRY:
            passed = context.retry_count < self.config.max_retry_attempts
            check = PolicyCheck(
                rule="max_retry_attempts",
                passed=passed,
                details=(
                    f"Retry #{context.retry_count + 1} vs max "
                    f"{self.config.max_retry_attempts}"
                )
            )
            checks.append(check)
            if not passed:
                blocking_rules.append("max_retry_attempts")

        # Rule 7: Discount cap
        if action.discount_percentage > 0:
            passed = action.discount_percentage <= self.config.max_discount_percentage
            check = PolicyCheck(
                rule="max_discount",
                passed=passed,
                details=(
                    f"Discount {action.discount_percentage:.1f}% vs cap "
                    f"{self.config.max_discount_percentage:.1f}%"
                )
            )
            checks.append(check)
            if not passed:
                blocking_rules.append("max_discount")

        # Rule 8: Minimum incremental value
        passed = (
            action.expected_incremental_value_paise
            >= self.config.min_incremental_value_paise
        )
        check = PolicyCheck(
            rule="min_incremental_value",
            passed=passed,
            details=(
                f"Expected ₹{action.expected_incremental_value_paise / 100:.0f} "
                f"vs min ₹{self.config.min_incremental_value_paise / 100:.0f}"
            )
        )
        checks.append(check)
        if not passed:
            blocking_rules.append("min_incremental_value")

        # Rule 9: Contact interval
        if context.last_contact_at is not None:
            now = datetime.now(timezone.utc)
            hours_since = (now - context.last_contact_at).total_seconds() / 3600
            passed = hours_since >= self.config.min_contact_interval_hours
            check = PolicyCheck(
                rule="min_contact_interval",
                passed=passed,
                details=(
                    f"Last contact {hours_since:.0f}h ago vs min "
                    f"{self.config.min_contact_interval_hours}h"
                )
            )
            checks.append(check)
            if not passed:
                blocking_rules.append("min_contact_interval")

        # Determine final status
        if blocking_rules:
            return PolicyResult(
                status=PolicyStatus.BLOCKED,
                checks=checks,
                blocking_rules=blocking_rules,
            )

        # Rule 10: Human approval threshold (amount-based)
        if context.amount_paise > self.config.human_approval_threshold_paise:
            checks.append(PolicyCheck(
                rule="human_approval_threshold",
                passed=True,
                details=(
                    f"Amount ₹{context.amount_paise / 100:,.0f} exceeds "
                    f"auto-approval threshold "
                    f"₹{self.config.human_approval_threshold_paise / 100:,.0f}"
                )
            ))
            return PolicyResult(
                status=PolicyStatus.REQUIRES_HUMAN,
                checks=checks,
                blocking_rules=[],
            )

        # All checks passed, amount below threshold
        checks.append(PolicyCheck(
            rule="amount_within_limit",
            passed=True,
            details=(
                f"Amount ₹{context.amount_paise / 100:,.0f} within "
                f"auto-approval limit"
            )
        ))
        return PolicyResult(
            status=PolicyStatus.APPROVED,
            checks=checks,
            blocking_rules=[],
        )
