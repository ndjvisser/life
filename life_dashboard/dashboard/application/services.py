"""
Dashboard application services - use case orchestration and business workflows.
"""

from django.utils import timezone

from ..domain.entities import UserProfile
from ..domain.repositories import UserProfileRepository, UserRepository
from ..domain.state_machines import OnboardingStateMachine
from ..domain.value_objects import OnboardingState, ProfileUpdateData


class UserService:
    """Service for user profile management commands."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        """
        Initialize the service with a user repository and a user profile repository.

        These repositories are stored on the instance for use by service methods.
        """
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        bio: str = "",
        location: str = "",
    ) -> tuple[int, UserProfile]:
        """
        Create a new user account and a corresponding user profile atomically.

        This operation is performed in a single transaction to ensure both the user
        and profile are created together, or neither is created if any part fails.

        Parameters:
            username: Desired unique username.
            email: User email address.
            password: Plain-text password (repository is responsible for hashing).
            first_name: Optional first name (defaults to empty string).
            last_name: Optional last name (defaults to empty string).
            bio: Optional user bio (defaults to empty string).
            location: Optional user location (defaults to empty string).

        Returns:
            Tuple[int, UserProfile]: The newly created user's id and the saved UserProfile instance.

        Raises:
            Exception: If user or profile creation fails.
        """
        return self.user_repo.create_user_with_profile(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            location=location,
        )

    def update_profile(
        self, user_id: int, update_data: ProfileUpdateData
    ) -> UserProfile:
        """
        Update a user's profile and propagate certain changes to the underlying user record.

        Updates the persisted UserProfile identified by user_id using fields from update_data.
        Fields on the profile are applied via update_data.to_dict(); the profile's updated_at
        timestamp is set to the current UTC time. If update_data contains first_name,
        last_name, or email (non-None), those values are also forwarded to the user repository
        to update the related User record.

        Parameters:
            user_id (int): Identifier of the user whose profile will be updated.
            update_data (ProfileUpdateData): Data object containing profile fields to apply.
                Fields set to None are treated as "no change" for propagation to the User model.

        Returns:
            UserProfile: The saved, updated profile.

        Raises:
            ValueError: If no profile exists for the given user_id.
        """
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        # Update profile fields
        profile.update_profile(**update_data.to_dict())
        profile.updated_at = timezone.now()

        # Also update User model fields if needed
        user_updates = {}
        if update_data.first_name is not None:
            user_updates["first_name"] = update_data.first_name
        if update_data.last_name is not None:
            user_updates["last_name"] = update_data.last_name
        if update_data.email is not None:
            user_updates["email"] = update_data.email

        if user_updates:
            self.user_repo.update_user(user_id, **user_updates)

        return self.profile_repo.save(profile)

    def add_experience(self, user_id: int, points: int) -> tuple[UserProfile, bool]:
        """
        Add experience points to a user's profile and persist the updated profile.

        This updates the profile's experience and level via domain logic, refreshes the profile's updated_at timestamp, saves the profile, and returns the saved profile along with a flag indicating whether a level-up occurred.

        Parameters:
            user_id (int): ID of the user whose profile will be updated.
            points (int): Number of experience points to add.

        Returns:
            Tuple[UserProfile, bool]: (saved_profile, level_up_occurred)

        Raises:
            ValueError: If no profile exists for the given user_id.
        """
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        # Add experience using domain logic
        new_level, level_up_occurred = profile.add_experience(points)
        profile.updated_at = timezone.now()

        # Save updated profile
        updated_profile = self.profile_repo.save(profile)

        return updated_profile, level_up_occurred

    def get_profile(self, user_id: int) -> UserProfile | None:
        """Get user profile by user ID."""
        return self.profile_repo.get_by_user_id(user_id)

    def get_profile_by_username(self, username: str) -> UserProfile | None:
        """
        Return the user's profile for the given username.

        Returns None if no profile is found for the provided username.
        """
        return self.profile_repo.get_by_username(username)


class AuthenticationService:
    """Service for user authentication workflows."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        """
        Initialize the service with a user repository and a user profile repository.

        These repositories are stored on the instance for use by service methods.
        """
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def authenticate(
        self, username: str, password: str
    ) -> tuple[int, UserProfile] | None:
        """
        Authenticate the provided username and password and return the authenticated user's id and profile.

        Attempts authentication via the user repository; on success fetches the associated UserProfile from the profile repository and returns (user_id, profile). Returns None if credentials are invalid or if no profile is found for the authenticated user.
        """
        user_id = self.user_repo.authenticate_user(username, password)
        if not user_id:
            return None

        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            # This shouldn't happen, but handle gracefully
            return None

        return user_id, profile

    def get_user_data(self, user_id: int) -> dict | None:
        """
        Return raw user record used for session management.

        Returns:
            dict or None: The user data dictionary returned by the user repository, or None if no user exists with the given ID.
        """
        return self.user_repo.get_user_by_id(user_id)


class OnboardingService:
    """Service for managing user onboarding workflow."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        """
        Initialize the service with a user repository and a user profile repository.

        These repositories are stored on the instance for use by service methods.
        """
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def get_onboarding_state(self, user_id: int) -> OnboardingStateMachine:
        """
        Return the user's current onboarding state as an OnboardingStateMachine.

        Uses the user's profile as a heuristic (no persistent onboarding state stored):
        - If no profile exists -> OnboardingState.REGISTRATION
        - If profile exists but both first_name and last_name are empty -> OnboardingState.PROFILE_SETUP
        - Otherwise -> OnboardingState.DASHBOARD

        Returns:
            OnboardingStateMachine: state machine seeded with the determined onboarding state.
        """
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return OnboardingStateMachine(OnboardingState.REGISTRATION)

        # Simple heuristic to determine onboarding state
        # In a real implementation, you'd store this explicitly
        if not profile.first_name and not profile.last_name:
            return OnboardingStateMachine(OnboardingState.PROFILE_SETUP)

        # For now, assume completed if profile has basic info
        return OnboardingStateMachine(OnboardingState.DASHBOARD)

    def advance_onboarding(
        self, user_id: int, target_state: OnboardingState
    ) -> OnboardingStateMachine:
        """
        Advance the user's onboarding state to the given target and return the resulting state machine.

        Attempts to transition the user's current OnboardingStateMachine to `target_state` and returns the updated machine.
        State changes are not persisted by this method (persistence is intentionally omitted).

        Parameters:
            user_id: The user's numeric identifier.
            target_state: The desired OnboardingState to transition to.

        Returns:
            The updated OnboardingStateMachine after the transition.

        Raises:
            OnboardingTransitionError: If the transition from the current state to `target_state` is invalid.
        """
        current_state_machine = self.get_onboarding_state(user_id)
        current_state_machine.transition_to(target_state)

        # In a real implementation, you'd persist the state change
        # For now, we just return the updated state machine

        return current_state_machine
