"""
Unit tests for the Workflow State Machine.

Tests valid transitions, invalid transitions, and terminal states.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from domain.workflow import WorkflowStateMachine, InvalidTransitionError
from events.event_types import WorkflowState


class TestValidTransitions:
    """Test that all expected transitions are allowed."""

    def test_none_to_detected(self):
        assert WorkflowStateMachine.validate_transition(None, WorkflowState.DETECTED)

    def test_detected_to_analyzing(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.DETECTED, WorkflowState.ANALYZING
        )

    def test_analyzing_to_recommended(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.ANALYZING, WorkflowState.RECOMMENDED
        )

    def test_recommended_to_policy_check(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.RECOMMENDED, WorkflowState.POLICY_CHECK
        )

    def test_policy_check_to_approved(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.POLICY_CHECK, WorkflowState.APPROVED
        )

    def test_policy_check_to_pending_approval(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.POLICY_CHECK, WorkflowState.PENDING_APPROVAL
        )

    def test_policy_check_to_blocked(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.POLICY_CHECK, WorkflowState.BLOCKED
        )

    def test_pending_approval_to_approved(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.PENDING_APPROVAL, WorkflowState.APPROVED
        )

    def test_pending_approval_to_blocked(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.PENDING_APPROVAL, WorkflowState.BLOCKED
        )

    def test_approved_to_executing(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.APPROVED, WorkflowState.EXECUTING
        )

    def test_executing_to_waiting_outcome(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.EXECUTING, WorkflowState.WAITING_OUTCOME
        )

    def test_waiting_outcome_to_recovered(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.WAITING_OUTCOME, WorkflowState.RECOVERED
        )

    def test_waiting_outcome_to_failed(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.WAITING_OUTCOME, WorkflowState.FAILED
        )

    def test_waiting_outcome_to_expired(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.WAITING_OUTCOME, WorkflowState.EXPIRED
        )

    def test_detected_to_escalated(self):
        assert WorkflowStateMachine.validate_transition(
            WorkflowState.DETECTED, WorkflowState.ESCALATED
        )


class TestInvalidTransitions:
    """Test that invalid transitions are rejected."""

    def test_cannot_skip_analyzing(self):
        with pytest.raises(InvalidTransitionError):
            WorkflowStateMachine.validate_transition(
                WorkflowState.DETECTED, WorkflowState.RECOMMENDED
            )

    def test_cannot_go_backwards(self):
        with pytest.raises(InvalidTransitionError):
            WorkflowStateMachine.validate_transition(
                WorkflowState.ANALYZING, WorkflowState.DETECTED
            )

    def test_cannot_execute_from_blocked(self):
        with pytest.raises(InvalidTransitionError):
            WorkflowStateMachine.validate_transition(
                WorkflowState.BLOCKED, WorkflowState.EXECUTING
            )

    def test_cannot_recover_from_failed(self):
        with pytest.raises(InvalidTransitionError):
            WorkflowStateMachine.validate_transition(
                WorkflowState.FAILED, WorkflowState.RECOVERED
            )


class TestTerminalStates:
    """Test terminal state detection."""

    def test_recovered_is_terminal(self):
        assert WorkflowStateMachine.is_terminal(WorkflowState.RECOVERED)

    def test_failed_is_terminal(self):
        assert WorkflowStateMachine.is_terminal(WorkflowState.FAILED)

    def test_blocked_is_terminal(self):
        assert WorkflowStateMachine.is_terminal(WorkflowState.BLOCKED)

    def test_expired_is_terminal(self):
        assert WorkflowStateMachine.is_terminal(WorkflowState.EXPIRED)

    def test_escalated_is_terminal(self):
        assert WorkflowStateMachine.is_terminal(WorkflowState.ESCALATED)

    def test_detected_is_not_terminal(self):
        assert not WorkflowStateMachine.is_terminal(WorkflowState.DETECTED)

    def test_analyzing_is_not_terminal(self):
        assert not WorkflowStateMachine.is_terminal(WorkflowState.ANALYZING)


class TestCanTransition:
    """Test the non-raising can_transition method."""

    def test_valid_returns_true(self):
        assert WorkflowStateMachine.can_transition(
            WorkflowState.DETECTED, WorkflowState.ANALYZING
        )

    def test_invalid_returns_false(self):
        assert not WorkflowStateMachine.can_transition(
            WorkflowState.DETECTED, WorkflowState.RECOVERED
        )


class TestGetValidTransitions:
    """Test getting valid transitions from a state."""

    def test_detected_has_two_transitions(self):
        valid = WorkflowStateMachine.get_valid_transitions(WorkflowState.DETECTED)
        assert WorkflowState.ANALYZING in valid
        assert WorkflowState.ESCALATED in valid
        assert len(valid) == 2

    def test_terminal_has_no_transitions(self):
        valid = WorkflowStateMachine.get_valid_transitions(WorkflowState.RECOVERED)
        assert len(valid) == 0
