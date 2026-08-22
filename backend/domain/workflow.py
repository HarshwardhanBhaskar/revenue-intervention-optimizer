"""
Workflow State Machine — enforces valid state transitions.

No state transition happens without validation.
Every transition creates an audit event.
"""

from events.event_types import WorkflowState, VALID_TRANSITIONS


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, current_state: WorkflowState | None, target_state: WorkflowState):
        self.current_state = current_state
        self.target_state = target_state
        current = current_state.value if current_state else "None"
        super().__init__(
            f"Invalid state transition: {current} → {target_state.value}"
        )


class WorkflowStateMachine:
    """
    Enforces valid workflow state transitions.

    The state machine is the single source of truth for what
    transitions are allowed. It does NOT make decisions about
    which transition to take — that's the recovery engine's job.
    """

    @staticmethod
    def validate_transition(
        current_state: WorkflowState | None,
        target_state: WorkflowState,
    ) -> bool:
        """
        Check if a state transition is valid.

        Returns True if valid, raises InvalidTransitionError if not.
        """
        valid_targets = VALID_TRANSITIONS.get(current_state, set())

        if target_state not in valid_targets:
            raise InvalidTransitionError(current_state, target_state)

        return True

    @staticmethod
    def can_transition(
        current_state: WorkflowState | None,
        target_state: WorkflowState,
    ) -> bool:
        """Check if a transition is valid without raising."""
        valid_targets = VALID_TRANSITIONS.get(current_state, set())
        return target_state in valid_targets

    @staticmethod
    def get_valid_transitions(
        current_state: WorkflowState | None,
    ) -> set[WorkflowState]:
        """Get all valid target states from the current state."""
        return VALID_TRANSITIONS.get(current_state, set())

    @staticmethod
    def is_terminal(state: WorkflowState) -> bool:
        """Check if a state is terminal (no further transitions possible)."""
        return len(VALID_TRANSITIONS.get(state, set())) == 0
