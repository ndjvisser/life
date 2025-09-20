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
        """
        Initialize the instance's valid onboarding state transitions after dataclass construction.
        
        Sets self._VALID_TRANSITIONS to a mapping from each OnboardingState to the set of allowed next states.
        The mapping encodes the workflow (REGISTRATION -> PROFILE_SETUP -> INITIAL_GOALS -> DASHBOARD),
        with DASHBOARD as a terminal state (no outgoing transitions).
        """
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
        Transition to the given onboarding state after validating the move.
        
        If the transition is not allowed the current state is left unchanged.
        
        Parameters:
            target_state (OnboardingState): Desired next state.
        
        Raises:
            OnboardingTransitionError: If transitioning from the current state to `target_state` is invalid.
        """
        if not self.can_transition_to(target_state):
            raise OnboardingTransitionError(
                f"Cannot transition from {self.current_state.value} to {target_state.value}"
            )

        self.current_state = target_state

    def complete_registration(self) -> None:
        """
        Mark the registration step complete by transitioning the machine to PROFILE_SETUP.
        
        Raises:
            OnboardingTransitionError: If the transition to PROFILE_SETUP is not allowed from the current state.
        """
        self.transition_to(OnboardingState.PROFILE_SETUP)

    def complete_profile_setup(self, skip_goals: bool = False) -> None:
        """
        Advance the machine from PROFILE_SETUP to the next onboarding step.
        
        If skip_goals is True, transition directly to DASHBOARD; otherwise transition to INITIAL_GOALS.
        
        Parameters:
            skip_goals (bool): When True, bypass the INITIAL_GOALS step and go straight to DASHBOARD.
        
        Raises:
            OnboardingTransitionError: If the requested transition is invalid from the current state.
        """
        if skip_goals:
            self.transition_to(OnboardingState.DASHBOARD)
        else:
            self.transition_to(OnboardingState.INITIAL_GOALS)

    def complete_initial_goals(self) -> None:
        """
        Mark the initial-goals step as complete by transitioning the state machine to DASHBOARD.
        
        Raises:
            OnboardingTransitionError: If the transition is not permitted from the current state.
        """
        self.transition_to(OnboardingState.DASHBOARD)

    def skip_to_dashboard(self) -> None:
        """
        Skip any remaining onboarding steps and set the state to DASHBOARD.
        
        Only permitted when the current state is PROFILE_SETUP or INITIAL_GOALS. On success this updates the machine's current_state to OnboardingState.DASHBOARD.
        
        Raises:
            OnboardingTransitionError: If the current state does not allow skipping to the dashboard.
        """
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
        """
        Return True if onboarding has reached the terminal DASHBOARD state.
        
        This property indicates whether the onboarding workflow is finished by checking
        if the machine's current_state equals OnboardingState.DASHBOARD.
        """
        return self.current_state == OnboardingState.DASHBOARD

    @property
    def next_step(self) -> Optional[OnboardingState]:
        """
        Return the next logical onboarding state from the current state.
        
        Checks allowed transitions for the current state and returns a single "primary" next step according to priority:
        PROFILE_SETUP → INITIAL_GOALS → DASHBOARD. If there are no valid next states (terminal state), returns None.
        
        Returns:
            Optional[OnboardingState]: The preferred next state, or None if onboarding is complete or no transitions are available.
        """
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
        """
        Return the user's onboarding completion as a percentage.
        
        Maps the current onboarding state to a float progress value:
        - REGISTRATION -> 0.0
        - PROFILE_SETUP -> 33.3
        - INITIAL_GOALS -> 66.7
        - DASHBOARD -> 100.0
        
        Returns:
            float: Progress percentage for the current state. If the current state is not recognized, returns 0.0.
        """
        progress_map = {
            OnboardingState.REGISTRATION: 0.0,
            OnboardingState.PROFILE_SETUP: 33.3,
            OnboardingState.INITIAL_GOALS: 66.7,
            OnboardingState.DASHBOARD: 100.0,
        }
        return progress_map.get(self.current_state, 0.0)
