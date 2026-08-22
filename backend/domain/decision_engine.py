"""
Decision Engine — Economic value computation and action ranking.

This is the intellectual core of the system. For each possible recovery
action, it computes:

    ExpectedValue(action) = P(recovery|action) × Amount - Cost(action) - DiscountCost(action)
    IncrementalValue(action) = ExpectedValue(action) - ExpectedValue(DO_NOTHING)

The system selects argmax(IncrementalValue) subject to policy constraints.
If the best action's incremental value < minimum threshold, it selects DO_NOTHING.

The decision engine uses ML model predictions but NEVER makes policy decisions.
Those are strictly handled by the PolicyEngine.
"""

from dataclasses import dataclass, field
from typing import Optional

from events.event_types import ActionType


@dataclass
class ActionEconomics:
    """Economic analysis of a single action."""
    action_type: ActionType
    probability: float                  # P(recovery | action)
    expected_revenue_paise: int         # P × Amount
    action_cost_paise: int              # Fixed cost of intervention
    discount_percentage: float          # Discount offered (0 for non-discount actions)
    discount_cost_paise: int            # P × Amount × discount%
    expected_net_value_paise: int       # Revenue - ActionCost - DiscountCost
    baseline_expected_paise: int        # P(recovery|do_nothing) × Amount
    incremental_value_paise: int        # NetValue - BaselineExpected
    confidence: float = 0.0            # Model confidence

    @property
    def incremental_value_rupees(self) -> float:
        return self.incremental_value_paise / 100

    @property
    def amount_display(self) -> str:
        return f"₹{self.incremental_value_paise / 100:,.0f}"

    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type.value,
            "probability": round(self.probability, 4),
            "expected_revenue": self.expected_revenue_paise,
            "action_cost": self.action_cost_paise,
            "discount_percentage": self.discount_percentage,
            "discount_cost": self.discount_cost_paise,
            "expected_net_value": self.expected_net_value_paise,
            "baseline_expected": self.baseline_expected_paise,
            "incremental_value": self.incremental_value_paise,
            "confidence": round(self.confidence, 4),
        }


@dataclass
class ActionRanking:
    """Ranked list of actions with their economic analysis."""
    rankings: list[ActionEconomics] = field(default_factory=list)
    recommended_action: Optional[ActionType] = None
    recommended_incremental_value_paise: int = 0

    def to_dict(self) -> dict:
        return {
            "recommended_action": (
                self.recommended_action.value if self.recommended_action else None
            ),
            "recommended_incremental_value": self.recommended_incremental_value_paise,
            "rankings": [r.to_dict() for r in self.rankings],
        }


# Action costs in paise (configurable per deployment)
DEFAULT_ACTION_COSTS: dict[ActionType, int] = {
    ActionType.DO_NOTHING: 0,
    ActionType.RETRY: 1_000,            # ₹10 — payment gateway cost
    ActionType.PAYMENT_LINK: 2_000,     # ₹20 — creation + delivery cost
    ActionType.REMINDER: 500,           # ₹5 — SMS/email cost
    ActionType.DISCOUNT: 2_000,         # ₹20 — same as payment link + admin
    ActionType.HUMAN_REVIEW: 10_000,    # ₹100 — human time cost
}

# Default discount percentages for the DISCOUNT action
DEFAULT_DISCOUNT_PERCENTAGE = 5.0


class DecisionEngine:
    """
    Computes expected economic value and ranks recovery actions.

    Uses ML model predictions to estimate P(recovery|action) for each action,
    then applies the economic value function to rank them.

    The decision engine is SEPARATE from the policy engine.
    It recommends the economically optimal action. The policy engine
    then determines if that action is allowed.
    """

    def __init__(
        self,
        action_costs: Optional[dict[ActionType, int]] = None,
        default_discount_pct: float = DEFAULT_DISCOUNT_PERCENTAGE,
        merchant_margin_pct: float = 1.0,
    ):
        self.action_costs = action_costs or DEFAULT_ACTION_COSTS.copy()
        self.default_discount_pct = default_discount_pct
        self.merchant_margin_pct = merchant_margin_pct

    def compute_action_economics(
        self,
        action_type: ActionType,
        amount_paise: int,
        p_recovery: float,
        p_baseline: float,
        discount_pct: float = 0.0,
        confidence: float = 1.0,
    ) -> ActionEconomics:
        """
        Compute the economic value of a single action.

        Formula:
            ExpectedRevenue = P(recovery|action) × Amount × MerchantMargin
            DiscountCost = P(recovery|action) × Amount × DiscountPct
                          (only pay discount if recovery succeeds)
            ExpectedNetValue = ExpectedRevenue - ActionCost - DiscountCost
            BaselineExpected = P(recovery|do_nothing) × Amount × MerchantMargin
            IncrementalValue = ExpectedNetValue - BaselineExpected
        """
        action_cost = self.action_costs.get(action_type, 0)

        expected_revenue = int(p_recovery * amount_paise * self.merchant_margin_pct)

        # Discount cost is only incurred if recovery succeeds
        discount_cost = int(p_recovery * amount_paise * (discount_pct / 100.0))

        expected_net_value = expected_revenue - action_cost - discount_cost

        baseline_expected = int(p_baseline * amount_paise * self.merchant_margin_pct)

        incremental_value = expected_net_value - baseline_expected

        return ActionEconomics(
            action_type=action_type,
            probability=p_recovery,
            expected_revenue_paise=expected_revenue,
            action_cost_paise=action_cost,
            discount_percentage=discount_pct,
            discount_cost_paise=discount_cost,
            expected_net_value_paise=expected_net_value,
            baseline_expected_paise=baseline_expected,
            incremental_value_paise=incremental_value,
            confidence=confidence,
        )

    def evaluate_actions(
        self,
        amount_paise: int,
        predictions: dict[ActionType, float],
        confidences: Optional[dict[ActionType, float]] = None,
        min_incremental_value_paise: int = 0,
    ) -> ActionRanking:
        """
        Evaluate all possible actions and rank by incremental value.

        Args:
            amount_paise: Transaction amount in paise
            predictions: Dict mapping ActionType → P(recovery|action)
            confidences: Optional dict mapping ActionType → model confidence
            min_incremental_value_paise: Minimum incremental value to recommend action

        Returns:
            ActionRanking with sorted actions and recommendation
        """
        if confidences is None:
            confidences = {a: 1.0 for a in predictions}

        # Baseline probability is always the DO_NOTHING prediction
        p_baseline = predictions.get(ActionType.DO_NOTHING, 0.0)

        rankings: list[ActionEconomics] = []

        for action_type, p_recovery in predictions.items():
            # Determine discount percentage
            discount_pct = (
                self.default_discount_pct
                if action_type == ActionType.DISCOUNT
                else 0.0
            )

            economics = self.compute_action_economics(
                action_type=action_type,
                amount_paise=amount_paise,
                p_recovery=p_recovery,
                p_baseline=p_baseline,
                discount_pct=discount_pct,
                confidence=confidences.get(action_type, 1.0),
            )
            rankings.append(economics)

        # Sort by incremental value descending
        rankings.sort(key=lambda x: x.incremental_value_paise, reverse=True)

        # Select recommendation
        best = rankings[0] if rankings else None

        if best and best.incremental_value_paise >= min_incremental_value_paise:
            recommended_action = best.action_type
            recommended_incremental = best.incremental_value_paise
        else:
            # Best action doesn't meet threshold — do nothing
            recommended_action = ActionType.DO_NOTHING
            recommended_incremental = 0

        return ActionRanking(
            rankings=rankings,
            recommended_action=recommended_action,
            recommended_incremental_value_paise=recommended_incremental,
        )

    def simulate_discount_scenarios(
        self,
        amount_paise: int,
        p_baseline: float,
        p_discount_base: float,
        discount_percentages: list[float] = None,
    ) -> list[ActionEconomics]:
        """
        Simulate multiple discount scenarios for the Decision Lab.

        For each discount percentage, estimates the recovery probability
        (assumes higher discount → higher probability, with diminishing returns)
        and computes economics.
        """
        if discount_percentages is None:
            discount_percentages = [2.0, 5.0, 8.0, 10.0]

        scenarios = []
        for pct in discount_percentages:
            # Simple model: each 1% discount adds ~1.5% probability, diminishing
            uplift_per_pct = 0.015 * (1 - pct / 20)  # Diminishing returns
            p_recovery = min(p_discount_base + uplift_per_pct * pct, 0.99)

            economics = self.compute_action_economics(
                action_type=ActionType.DISCOUNT,
                amount_paise=amount_paise,
                p_recovery=p_recovery,
                p_baseline=p_baseline,
                discount_pct=pct,
            )
            scenarios.append(economics)

        return scenarios
