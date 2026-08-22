"""
Event Types — Enum of all system events.

Every significant event in the system must be one of these types.
Used by the audit engine to create immutable event records.
"""

from enum import Enum


class EventType(str, Enum):
    """All event types in the system."""

    # --- Payment lifecycle ---
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"

    # --- Recovery workflow ---
    RECOVERY_DETECTED = "recovery.detected"
    RECOVERY_FEATURES_COMPUTED = "recovery.features_computed"
    RECOVERY_SCORED = "recovery.scored"
    RECOVERY_RECOMMENDED = "recovery.recommended"
    RECOVERY_POLICY_CHECKED = "recovery.policy_checked"
    RECOVERY_APPROVAL_REQUESTED = "recovery.approval_requested"
    RECOVERY_APPROVED = "recovery.approved"
    RECOVERY_REJECTED = "recovery.rejected"
    RECOVERY_BLOCKED = "recovery.blocked"
    RECOVERY_DO_NOTHING = "recovery.do_nothing"
    RECOVERY_EXECUTING = "recovery.executing"
    RECOVERY_EXECUTED = "recovery.executed"
    RECOVERY_OUTCOME_RECEIVED = "recovery.outcome_received"
    RECOVERY_COMPLETED = "recovery.completed"
    RECOVERY_FAILED = "recovery.failed"
    RECOVERY_EXPIRED = "recovery.expired"
    RECOVERY_ESCALATED = "recovery.escalated"
    RECOVERY_STOPPED = "recovery.stopped"

    # --- Policy ---
    POLICY_UPDATED = "policy.updated"

    # --- Model ---
    MODEL_INFERENCE = "model.inference"
    MODEL_FALLBACK = "model.fallback"
    MODEL_UNAVAILABLE = "model.unavailable"

    # --- Webhook ---
    WEBHOOK_RECEIVED = "webhook.received"
    WEBHOOK_DUPLICATE = "webhook.duplicate"
    WEBHOOK_INVALID = "webhook.invalid"
    WEBHOOK_PROCESSING_FAILED = "webhook.processing_failed"


class WorkflowState(str, Enum):
    """Recovery workflow states."""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RECOMMENDED = "recommended"
    POLICY_CHECK = "policy_check"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    BLOCKED = "blocked"
    EXECUTING = "executing"
    WAITING_OUTCOME = "waiting_outcome"
    RECOVERED = "recovered"
    FAILED = "failed"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    STOPPED = "stopped"


class ActionType(str, Enum):
    """Recovery action types."""
    DO_NOTHING = "do_nothing"
    RETRY = "retry"
    PAYMENT_LINK = "payment_link"
    REMINDER = "reminder"
    DISCOUNT = "discount"
    HUMAN_REVIEW = "human_review"


class PolicyStatus(str, Enum):
    """Policy evaluation result."""
    APPROVED = "approved"
    BLOCKED = "blocked"
    REQUIRES_HUMAN = "requires_human"


class RiskStatus(str, Enum):
    """Risk firewall evaluation result."""
    CLEAR = "clear"
    BLOCKED = "blocked"
    ESCALATE = "escalate"


class ActionStatus(str, Enum):
    """Recovery action execution status."""
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalStatus(str, Enum):
    """Human approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Valid state transitions — enforced by the workflow state machine
VALID_TRANSITIONS: dict[WorkflowState | None, set[WorkflowState]] = {
    None: {WorkflowState.DETECTED},
    WorkflowState.DETECTED: {WorkflowState.ANALYZING, WorkflowState.ESCALATED},
    WorkflowState.ANALYZING: {WorkflowState.RECOMMENDED, WorkflowState.ESCALATED},
    WorkflowState.RECOMMENDED: {WorkflowState.POLICY_CHECK},
    WorkflowState.POLICY_CHECK: {
        WorkflowState.APPROVED,
        WorkflowState.PENDING_APPROVAL,
        WorkflowState.BLOCKED,
    },
    WorkflowState.PENDING_APPROVAL: {WorkflowState.APPROVED, WorkflowState.BLOCKED},
    WorkflowState.APPROVED: {WorkflowState.EXECUTING},
    WorkflowState.EXECUTING: {WorkflowState.WAITING_OUTCOME},
    WorkflowState.WAITING_OUTCOME: {
        WorkflowState.RECOVERED,
        WorkflowState.FAILED,
        WorkflowState.EXPIRED,
    },
    # Terminal states — no transitions out
    WorkflowState.BLOCKED: set(),
    WorkflowState.RECOVERED: set(),
    WorkflowState.FAILED: set(),
    WorkflowState.EXPIRED: set(),
    WorkflowState.ESCALATED: set(),
    WorkflowState.STOPPED: set(),
}
