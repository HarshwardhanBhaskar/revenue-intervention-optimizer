"""
Risk Firewall — Pre-execution safety checks.

Runs BEFORE the policy engine. Acts as a circuit breaker for
hard-stop conditions that override everything else.
"""

from dataclasses import dataclass, field
from events.event_types import RiskStatus, ActionType


@dataclass
class RiskCheck:
    """Result of a single risk check."""
    check: str
    passed: bool
    details: str
    severity: str = "high"  # high, medium, low


@dataclass
class RiskResult:
    """Aggregate risk evaluation result."""
    status: RiskStatus
    checks: list[RiskCheck] = field(default_factory=list)
    blocking_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "checks": [
                {
                    "check": c.check,
                    "passed": c.passed,
                    "details": c.details,
                    "severity": c.severity,
                }
                for c in self.checks
            ],
            "blocking_checks": self.blocking_checks,
        }


class RiskFirewall:
    """
    Hard safety checks that run before policy evaluation.

    These are non-negotiable blocks:
    1. Fraud signal → BLOCK
    2. Concurrent recovery in progress → BLOCK
    3. Action already executed (idempotency) → BLOCK
    4. Model confidence below minimum → ESCALATE
    """

    def __init__(self, min_model_confidence: float = 0.3):
        self.min_model_confidence = min_model_confidence

    def evaluate(
        self,
        action_type: ActionType,
        has_fraud_signal: bool = False,
        has_concurrent_recovery: bool = False,
        action_already_executed: bool = False,
        model_confidence: float = 1.0,
        model_available: bool = True,
    ) -> RiskResult:
        """
        Evaluate risk checks.

        Returns CLEAR, BLOCKED, or ESCALATE.
        """
        checks: list[RiskCheck] = []
        blocking: list[str] = []

        # DO_NOTHING and HUMAN_REVIEW always pass risk checks
        if action_type in (ActionType.DO_NOTHING, ActionType.HUMAN_REVIEW):
            checks.append(RiskCheck(
                check="safe_action",
                passed=True,
                details=f"{action_type.value} is always risk-clear",
            ))
            return RiskResult(status=RiskStatus.CLEAR, checks=checks)

        # Check 1: Fraud signal
        if has_fraud_signal:
            checks.append(RiskCheck(
                check="fraud_signal",
                passed=False,
                details="Fraud signal detected — all actions blocked",
                severity="high",
            ))
            blocking.append("fraud_signal")

        # Check 2: Concurrent recovery
        if has_concurrent_recovery:
            checks.append(RiskCheck(
                check="concurrent_recovery",
                passed=False,
                details="Another recovery action is already in progress for this payment",
                severity="high",
            ))
            blocking.append("concurrent_recovery")

        # Check 3: Idempotency (already executed)
        if action_already_executed:
            checks.append(RiskCheck(
                check="idempotency",
                passed=False,
                details="This action has already been executed",
                severity="high",
            ))
            blocking.append("idempotency")

        if blocking:
            return RiskResult(
                status=RiskStatus.BLOCKED,
                checks=checks,
                blocking_checks=blocking,
            )

        # Check 4: Model availability
        if not model_available:
            checks.append(RiskCheck(
                check="model_unavailable",
                passed=False,
                details="ML model is unavailable — escalating to human review",
                severity="medium",
            ))
            return RiskResult(
                status=RiskStatus.ESCALATE,
                checks=checks,
                blocking_checks=["model_unavailable"],
            )

        # Check 5: Model confidence
        if model_confidence < self.min_model_confidence:
            checks.append(RiskCheck(
                check="low_confidence",
                passed=False,
                details=(
                    f"Model confidence {model_confidence:.2f} below minimum "
                    f"{self.min_model_confidence:.2f} — escalating"
                ),
                severity="medium",
            ))
            return RiskResult(
                status=RiskStatus.ESCALATE,
                checks=checks,
                blocking_checks=["low_confidence"],
            )

        # All checks passed
        checks.append(RiskCheck(
            check="all_clear",
            passed=True,
            details="All risk checks passed",
        ))
        return RiskResult(status=RiskStatus.CLEAR, checks=checks)
