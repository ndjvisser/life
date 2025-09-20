"""
Dashboard domain state machines - pure Python state management.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Set

from .value_objects import OnboardingState


class OnboardingTransitionError(Exception):
    """Raised when an invalid onboarding transition is attempted."""

    pass


@dataclass
class OnboardingStateMachine:
    """
    State machine for user onboarding process.

    Manages transitions between onboarding states with validation.
    """

    current_state: OnboardingState = OnboardingState.REGISTRATION

    def __post_init__(self):
        """Initialize valid transitions after dataclass creation."""
        # Define valid transitions
        self._VALID_TRANSITIONS: Dict[OnboardingState, Set[OnboardingState]] = {
            OnboardingState.REGISTRATION: {OnboardingState.PROFILE_SETUP},
            OnboardingState.PROFILE_SETUP: {
                OnboardingState.INITIAL_GOALS,
                OnboardingState.DASHBOARD,
            },
            OnboardingState.INITIAL_GOALS: {OnboardingState.DASHBOARD},
            OnboardingState.DASHBOARD: set(),  # Terminal state
        }

    def can_transition_to(self, target_state: OnboardingState) -> bool:
        """Check if transition to target state is valid."""
        return target_state in self._VALID_TRANSITIONS.get(self.current_state, set())

    def transition_to(self, target_state: OnboardingState) -> None:
        """
        Transition to target state with validation.

        Args:
            target_state: The state to transition to

        Raises:
            OnboardingTransitionError: If transition is invalid
        """
        if not self.can_transition_to(target_state):
            raise OnboardingTransitionError(
                f"Cannot transition from {self.current_state.value} to {target_state.value}"
            )

        self.current_state = target_state

    def complete_registration(self) -> None:
        """Complete registration step."""
        self.transition_to(OnboardingState.PROFILE_SETUP)

    def complete_profile_setup(self, skip_goals: bool = False) -> None:
        """Complete profile setup step."""
        if skip_goals:
            self.transition_to(OnboardingState.DASHBOARD)
        else:
            self.transition_to(OnboardingState.INITIAL_GOALS)

    def complete_initial_goals(self) -> None:
        """Complete initial goals setup."""
        self.transition_to(OnboardingState.DASHBOARD)

    def skip_to_dashboard(self) -> None:
        """Skip remaining steps and go to dashboard (if allowed)."""
        if self.current_state in {
            OnboardingState.PROFILE_SETUP,
            OnboardingState.INITIAL_GOALS,
        }:
            self.transition_to(OnboardingState.DASHBOARD)
        else:
            raise OnboardingTransitionError(
                f"Cannot skip to dashboard from {self.current_state.value}"
            )

    @property
    def is_complete(self) -> bool:
        """Check if onboarding is complete."""
        return self.current_state == OnboardingState.DASHBOARD

    @property
    def next_step(self) -> Optional[OnboardingState]:
        """Get the next logical step in onboarding."""
        valid_transitions = self._VALID_TRANSITIONS.get(self.current_state, set())
        if not valid_transitions:
            return None

        # Return the "primary" next step
        if OnboardingState.PROFILE_SETUP in valid_transitions:
            return OnboardingState.PROFILE_SETUP
        elif OnboardingState.INITIAL_GOALS in valid_transitions:
            return OnboardingState.INITIAL_GOALS
        elif OnboardingState.DASHBOARD in valid_transitions:
            return OnboardingState.DASHBOARD

        return None

    def get_progress_percentage(self) -> float:
        """Get onboarding progress as percentage."""
        progress_map = {
            OnboardingState.REGISTRATION: 0.0,
            OnboardingState.PROFILE_SETUP: 33.3,
            OnboardingState.INITIAL_GOALS: 66.7,
            OnboardingState.DASHBOARD: 100.0,
        }
        return progress_map.get(self.current_state, 0.0)
