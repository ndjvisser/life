"""
Tests for dashboard domain layer - pure Python business logic tests.
"""

import pytest

from ..domain.entities import UserProfile
from ..domain.state_machines import OnboardingStateMachine, OnboardingTransitionError
from ..domain.value_objects import (
    ExperiencePoints,
    OnboardingState,
    ProfileUpdateData,
    UserLevel,
)


class TestUserProfile:
    """Test UserProfile domain entity."""

    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        assert profile.user_id == 1
        assert profile.username == "testuser"
        assert profile.experience_points == 0
        assert profile.level == 1

    def test_add_experience_valid(self):
        """Test adding valid experience points."""
        profile = UserProfile(user_id=1, username="testuser")

        new_level, level_up = profile.add_experience(500)

        assert profile.experience_points == 500
        assert profile.level == 1
        assert new_level == 1
        assert level_up is False

    def test_add_experience_level_up(self):
        """Test level up when adding experience."""
        profile = UserProfile(user_id=1, username="testuser")

        new_level, level_up = profile.add_experience(1500)

        assert profile.experience_points == 1500
        assert profile.level == 2
        assert new_level == 2
        assert level_up is True

    def test_add_experience_invalid_points(self):
        """Test adding invalid experience points."""
        profile = UserProfile(user_id=1, username="testuser")

        with pytest.raises(
            ValueError, match="Experience points must be a positive integer"
        ):
            profile.add_experience(-100)

        with pytest.raises(
            ValueError, match="Experience points must be a positive integer"
        ):
            profile.add_experience(0)

        with pytest.raises(
            ValueError, match="Experience points must be a positive integer"
        ):
            profile.add_experience("100")

    def test_add_experience_overflow_protection(self):
        """Test experience overflow protection."""
        profile = UserProfile(user_id=1, username="testuser")
        profile.experience_points = 2**31 - 100  # Near max

        new_level, level_up = profile.add_experience(200)

        assert profile.experience_points == 2**31 - 1  # Capped at max
        assert profile.level > 1

    def test_update_profile_valid_fields(self):
        """Test updating profile with valid fields."""
        profile = UserProfile(user_id=1, username="testuser")

        profile.update_profile(
            first_name="Updated", last_name="Name", email="updated@example.com"
        )

        assert profile.first_name == "Updated"
        assert profile.last_name == "Name"
        assert profile.email == "updated@example.com"

    def test_update_profile_invalid_field(self):
        """Test updating profile with invalid field."""
        profile = UserProfile(user_id=1, username="testuser")

        with pytest.raises(ValueError, match="Field 'invalid_field' is not allowed"):
            profile.update_profile(invalid_field="value")

    def test_full_name_property(self):
        """Test full name property."""
        profile = UserProfile(
            user_id=1, username="testuser", first_name="John", last_name="Doe"
        )

        assert profile.full_name == "John Doe"

    def test_experience_to_next_level(self):
        """Test experience to next level calculation."""
        profile = UserProfile(user_id=1, username="testuser")
        profile.experience_points = 750
        profile.level = 1

        assert profile.experience_to_next_level == 250  # 1000 - 750

    def test_level_progress_percentage(self):
        """Test level progress percentage calculation."""
        profile = UserProfile(user_id=1, username="testuser")
        profile.experience_points = 750
        profile.level = 1

        # Level 1: 0-1000 XP, currently at 750
        expected_percentage = (750 / 1000) * 100
        assert profile.level_progress_percentage == expected_percentage


class TestExperiencePoints:
    """Test ExperiencePoints value object."""

    def test_create_valid_experience_points(self):
        """Test creating valid experience points."""
        xp = ExperiencePoints(100)
        assert xp.value == 100

    def test_create_invalid_experience_points(self):
        """Test creating invalid experience points."""
        with pytest.raises(ValueError, match="Experience points must be an integer"):
            ExperiencePoints("100")

        with pytest.raises(ValueError, match="Experience points cannot be negative"):
            ExperiencePoints(-100)

        with pytest.raises(ValueError, match="Experience points exceed maximum value"):
            ExperiencePoints(2**31)

    def test_add_experience_points(self):
        """Test adding experience points."""
        xp = ExperiencePoints(100)
        new_xp = xp.add(50)

        assert new_xp.value == 150
        assert xp.value == 100  # Original unchanged (immutable)

    def test_add_invalid_points(self):
        """Test adding invalid points."""
        xp = ExperiencePoints(100)

        with pytest.raises(
            ValueError, match="Points to add must be a positive integer"
        ):
            xp.add(-50)

        with pytest.raises(
            ValueError, match="Points to add must be a positive integer"
        ):
            xp.add(0)

    def test_calculate_level(self):
        """Test level calculation from experience points."""
        assert ExperiencePoints(0).calculate_level() == 1
        assert ExperiencePoints(999).calculate_level() == 1
        assert ExperiencePoints(1000).calculate_level() == 2
        assert ExperiencePoints(2500).calculate_level() == 3


class TestUserLevel:
    """Test UserLevel value object."""

    def test_create_valid_level(self):
        """Test creating valid level."""
        level = UserLevel(5)
        assert level.value == 5

    def test_create_invalid_level(self):
        """Test creating invalid level."""
        with pytest.raises(ValueError, match="Level must be an integer"):
            UserLevel("5")

        with pytest.raises(ValueError, match="Level must be at least 1"):
            UserLevel(0)

        with pytest.raises(ValueError, match="Level exceeds maximum value"):
            UserLevel(1001)

    def test_from_experience(self):
        """Test creating level from experience points."""
        level = UserLevel.from_experience(2500)
        assert level.value == 3

    def test_experience_thresholds(self):
        """Test experience threshold calculations."""
        level = UserLevel(3)
        assert level.experience_threshold() == 2000  # (3-1) * 1000
        assert level.next_level_threshold() == 3000  # 3 * 1000


class TestProfileUpdateData:
    """Test ProfileUpdateData value object."""

    def test_create_valid_update_data(self):
        """Test creating valid update data."""
        data = ProfileUpdateData(
            first_name="John", last_name="Doe", email="john@example.com"
        )

        assert data.first_name == "John"
        assert data.last_name == "Doe"
        assert data.email == "john@example.com"

    def test_create_with_long_strings(self):
        """Test creating with strings that are too long."""
        with pytest.raises(ValueError, match="First name too long"):
            ProfileUpdateData(first_name="x" * 151)

        with pytest.raises(ValueError, match="Bio too long"):
            ProfileUpdateData(bio="x" * 501)

    def test_to_dict_excludes_none(self):
        """Test to_dict excludes None values."""
        data = ProfileUpdateData(
            first_name="John", last_name=None, email="john@example.com"
        )

        result = data.to_dict()
        assert result == {"first_name": "John", "email": "john@example.com"}
        assert "last_name" not in result


class TestOnboardingStateMachine:
    """Test OnboardingStateMachine."""

    def test_initial_state(self):
        """Test initial state."""
        sm = OnboardingStateMachine()
        assert sm.current_state == OnboardingState.REGISTRATION
        assert not sm.is_complete

    def test_valid_transitions(self):
        """Test valid state transitions."""
        sm = OnboardingStateMachine()

        # Registration -> Profile Setup
        assert sm.can_transition_to(OnboardingState.PROFILE_SETUP)
        sm.transition_to(OnboardingState.PROFILE_SETUP)
        assert sm.current_state == OnboardingState.PROFILE_SETUP

        # Profile Setup -> Initial Goals
        assert sm.can_transition_to(OnboardingState.INITIAL_GOALS)
        sm.transition_to(OnboardingState.INITIAL_GOALS)
        assert sm.current_state == OnboardingState.INITIAL_GOALS

        # Initial Goals -> Dashboard
        assert sm.can_transition_to(OnboardingState.DASHBOARD)
        sm.transition_to(OnboardingState.DASHBOARD)
        assert sm.current_state == OnboardingState.DASHBOARD
        assert sm.is_complete

    def test_invalid_transitions(self):
        """Test invalid state transitions."""
        sm = OnboardingStateMachine()

        # Cannot go directly from Registration to Dashboard
        assert not sm.can_transition_to(OnboardingState.DASHBOARD)

        with pytest.raises(OnboardingTransitionError):
            sm.transition_to(OnboardingState.DASHBOARD)

    def test_skip_to_dashboard(self):
        """Test skipping to dashboard."""
        sm = OnboardingStateMachine(OnboardingState.PROFILE_SETUP)

        sm.skip_to_dashboard()
        assert sm.current_state == OnboardingState.DASHBOARD
        assert sm.is_complete

    def test_skip_to_dashboard_invalid(self):
        """Test invalid skip to dashboard."""
        sm = OnboardingStateMachine(OnboardingState.REGISTRATION)

        with pytest.raises(OnboardingTransitionError):
            sm.skip_to_dashboard()

    def test_convenience_methods(self):
        """Test convenience transition methods."""
        sm = OnboardingStateMachine()

        sm.complete_registration()
        assert sm.current_state == OnboardingState.PROFILE_SETUP

        sm.complete_profile_setup(skip_goals=True)
        assert sm.current_state == OnboardingState.DASHBOARD

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        sm = OnboardingStateMachine()
        assert sm.get_progress_percentage() == 0.0

        sm.complete_registration()
        assert sm.get_progress_percentage() == 33.3

        sm.complete_profile_setup()
        assert sm.get_progress_percentage() == 66.7

        sm.complete_initial_goals()
        assert sm.get_progress_percentage() == 100.0

    def test_next_step(self):
        """Test next step calculation."""
        sm = OnboardingStateMachine()
        assert sm.next_step == OnboardingState.PROFILE_SETUP

        sm.complete_registration()
        assert sm.next_step == OnboardingState.INITIAL_GOALS

        sm.complete_profile_setup()
        assert sm.next_step == OnboardingState.DASHBOARD

        sm.complete_initial_goals()
        assert sm.next_step is None  # Complete
