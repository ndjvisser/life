"""
Dashboard application services - use case orchestration and business workflows.
"""

from datetime import datetime
from typing import Optional, Tuple

from ..domain.entities import UserProfile
from ..domain.repositories import UserProfileRepository, UserRepository
from ..domain.state_machines import OnboardingStateMachine
from ..domain.value_objects import OnboardingState, ProfileUpdateData


class UserService:
    """Service for user profile management commands."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> Tuple[int, UserProfile]:
        """
        Register a new user with profile.

        Returns:
            tuple: (user_id, user_profile)
        """
        # Create user account
        user_id = self.user_repo.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create user profile
        profile = UserProfile(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        saved_profile = self.profile_repo.create(profile)
        return user_id, saved_profile

    def update_profile(
        self, user_id: int, update_data: ProfileUpdateData
    ) -> UserProfile:
        """
        Update user profile with validation.

        Args:
            user_id: User ID
            update_data: Profile update data

        Returns:
            Updated UserProfile

        Raises:
            ValueError: If user not found or validation fails
        """
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        # Update profile fields
        profile.update_profile(**update_data.to_dict())
        profile.updated_at = datetime.utcnow()

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

    def add_experience(self, user_id: int, points: int) -> Tuple[UserProfile, bool]:
        """
        Add experience points to user profile.

        Args:
            user_id: User ID
            points: Experience points to add

        Returns:
            tuple: (updated_profile, level_up_occurred)

        Raises:
            ValueError: If user not found or invalid points
        """
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        # Add experience using domain logic
        new_level, level_up_occurred = profile.add_experience(points)
        profile.updated_at = datetime.utcnow()

        # Save updated profile
        updated_profile = self.profile_repo.save(profile)

        return updated_profile, level_up_occurred

    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        return self.profile_repo.get_by_user_id(user_id)

    def get_profile_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username."""
        return self.profile_repo.get_by_username(username)


class AuthenticationService:
    """Service for user authentication workflows."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def authenticate(
        self, username: str, password: str
    ) -> Optional[Tuple[int, UserProfile]]:
        """
        Authenticate user credentials.

        Returns:
            tuple: (user_id, user_profile) if successful, None if failed
        """
        user_id = self.user_repo.authenticate_user(username, password)
        if not user_id:
            return None

        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            # This shouldn't happen, but handle gracefully
            return None

        return user_id, profile

    def get_user_data(self, user_id: int) -> Optional[dict]:
        """Get user data for session management."""
        return self.user_repo.get_user_by_id(user_id)


class OnboardingService:
    """Service for managing user onboarding workflow."""

    def __init__(self, user_repo: UserRepository, profile_repo: UserProfileRepository):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def get_onboarding_state(self, user_id: int) -> OnboardingStateMachine:
        """
        Get current onboarding state for user.

        This is a simplified implementation - in a real system, you'd store
        the onboarding state in the database.
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
        Advance user's onboarding to target state.

        Args:
            user_id: User ID
            target_state: Target onboarding state

        Returns:
            Updated OnboardingStateMachine

        Raises:
            OnboardingTransitionError: If transition is invalid
        """
        current_state_machine = self.get_onboarding_state(user_id)
        current_state_machine.transition_to(target_state)

        # In a real implementation, you'd persist the state change
        # For now, we just return the updated state machine

        return current_state_machine
