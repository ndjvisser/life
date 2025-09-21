"""
Property-based tests for dashboard domain - using Hypothesis for comprehensive validation.
"""

import pytest

pytest.importorskip("hypothesis")
from hypothesis import assume, given
from hypothesis import strategies as st

from life_dashboard.dashboard.domain.entities import UserProfile
from life_dashboard.dashboard.domain.state_machines import OnboardingStateMachine
from life_dashboard.dashboard.domain.value_objects import (
    ExperiencePoints,
    OnboardingState,
    ProfileUpdateData,
    UserLevel,
)


@pytest.mark.property
@pytest.mark.domain
class TestUserProfileProperties:
    """Property-based tests for UserProfile entity."""

    @given(
        user_id=st.integers(min_value=1, max_value=1000000),
        username=st.text(min_size=1, max_size=150),
        experience_points=st.integers(min_value=0, max_value=2**31 - 1),
    )
    def test_user_profile_creation_always_valid_with_valid_inputs(
        self, user_id, username, experience_points
    ):
        """Test that UserProfile creation always succeeds with valid inputs."""
        assume(username.strip())  # Ensure username is not just whitespace

        profile = UserProfile(
            user_id=user_id,
            username=username.strip(),
            experience_points=experience_points,
        )

        assert profile.user_id == user_id
        assert profile.username == username.strip()
        assert profile.experience_points == experience_points
        assert profile.level >= 1

    @given(points=st.integers(min_value=1, max_value=1000000))
    def test_add_experience_always_increases_or_maintains_level(self, points):
        """Test that adding experience never decreases level."""
        profile = UserProfile(user_id=1, username="test")
        original_level = profile.level

        new_level, level_up = profile.add_experience(points)

        assert profile.level >= original_level
        assert new_level >= original_level
        assert level_up == (new_level > original_level)

    @given(
        initial_xp=st.integers(min_value=0, max_value=2**30),
        additional_xp=st.integers(min_value=1, max_value=1000000),
    )
    def test_experience_overflow_protection_always_caps_correctly(
        self, initial_xp, additional_xp
    ):
        """Test that experience overflow protection always works correctly."""
        profile = UserProfile(user_id=1, username="test", experience_points=initial_xp)

        profile.add_experience(additional_xp)

        # Experience should never exceed maximum
        assert profile.experience_points <= 2**31 - 1
        # Level should be calculated correctly from capped experience
        expected_level = max(1, (profile.experience_points // 1000) + 1)
        assert profile.level == expected_level

    @given(
        first_name=st.one_of(st.none(), st.text(max_size=150)),
        last_name=st.one_of(st.none(), st.text(max_size=150)),
        email=st.one_of(st.none(), st.text(max_size=254)),
        bio=st.one_of(st.none(), st.text(max_size=500)),
        location=st.one_of(st.none(), st.text(max_size=30)),
    )
    def test_update_profile_with_valid_fields_always_succeeds(
        self, first_name, last_name, email, bio, location
    ):
        """Test that updating profile with valid fields always succeeds."""
        profile = UserProfile(user_id=1, username="test")

        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if email is not None:
            update_data["email"] = email
        if bio is not None:
            update_data["bio"] = bio
        if location is not None:
            update_data["location"] = location

        profile.update_profile(**update_data)

        # Verify all fields were updated correctly
        for field, value in update_data.items():
            assert getattr(profile, field) == value

    @given(experience_points=st.integers(min_value=0, max_value=2**31 - 1))
    def test_level_progress_percentage_is_always_bounded(self, experience_points):
        """Test that level progress percentage is always between 0 and 100."""
        profile = UserProfile(
            user_id=1, username="test", experience_points=experience_points
        )

        progress = profile.level_progress_percentage

        assert 0.0 <= progress <= 100.0

    @given(experience_points=st.integers(min_value=0, max_value=2**31 - 1))
    def test_experience_to_next_level_is_always_non_negative(self, experience_points):
        """Test that experience to next level is always non-negative."""
        profile = UserProfile(
            user_id=1, username="test", experience_points=experience_points
        )

        remaining_xp = profile.experience_to_next_level

        assert remaining_xp >= 0


@pytest.mark.property
@pytest.mark.domain
class TestValueObjectProperties:
    """Property-based tests for value objects."""

    @given(experience_points=st.integers(min_value=0, max_value=2**31 - 1))
    def test_experience_points_accepts_valid_range(self, experience_points):
        """Test that ExperiencePoints accepts valid range."""
        xp = ExperiencePoints(experience_points)
        assert xp.value == experience_points
        assert xp.calculate_level() >= 1

    @given(experience_points=st.integers().filter(lambda x: x < 0 or x > 2**31 - 1))
    def test_experience_points_rejects_invalid_range(self, experience_points):
        """Test that ExperiencePoints rejects invalid range."""
        with pytest.raises(ValueError):
            ExperiencePoints(experience_points)

    @given(
        initial_xp=st.integers(min_value=0, max_value=2**30),
        additional_points=st.integers(min_value=1, max_value=1000000),
    )
    def test_experience_points_add_maintains_invariants(
        self, initial_xp, additional_points
    ):
        """Test that adding experience points maintains invariants."""
        xp = ExperiencePoints(initial_xp)
        new_xp = xp.add(additional_points)

        # New value should be greater than or equal to original
        assert new_xp.value >= xp.value
        # New value should not exceed maximum
        assert new_xp.value <= 2**31 - 1
        # Original should be unchanged (immutable)
        assert xp.value == initial_xp

    @given(level=st.integers(min_value=1, max_value=1000))
    def test_user_level_accepts_valid_range(self, level):
        """Test that UserLevel accepts valid range."""
        user_level = UserLevel(level)
        assert user_level.value == level
        assert user_level.experience_threshold() >= 0
        assert user_level.next_level_threshold() > user_level.experience_threshold()

    @given(level=st.integers().filter(lambda x: x < 1 or x > 1000))
    def test_user_level_rejects_invalid_range(self, level):
        """Test that UserLevel rejects invalid range."""
        with pytest.raises(ValueError):
            UserLevel(level)

    @given(
        experience_points=st.integers(min_value=0, max_value=999000)
    )  # Cap to avoid exceeding max level
    def test_user_level_from_experience_is_consistent(self, experience_points):
        """Test that UserLevel.from_experience is consistent with calculation."""
        level = UserLevel.from_experience(experience_points)
        expected_level = max(1, (experience_points // 1000) + 1)

        assert level.value == expected_level
        assert level.experience_threshold() <= experience_points
        if experience_points < 999000:  # Not at max level
            assert level.next_level_threshold() > experience_points

    @given(
        first_name=st.one_of(st.none(), st.text(max_size=150)),
        last_name=st.one_of(st.none(), st.text(max_size=150)),
        email=st.one_of(st.none(), st.text(max_size=254)),
        bio=st.one_of(st.none(), st.text(max_size=500)),
        location=st.one_of(st.none(), st.text(max_size=30)),
    )
    def test_profile_update_data_accepts_valid_lengths(
        self, first_name, last_name, email, bio, location
    ):
        """Test that ProfileUpdateData accepts valid field lengths."""
        data = ProfileUpdateData(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            location=location,
        )

        # Verify all fields are set correctly
        assert data.first_name == first_name
        assert data.last_name == last_name
        assert data.email == email
        assert data.bio == bio
        assert data.location == location

        # Verify to_dict excludes None values
        result_dict = data.to_dict()
        for _field, value in result_dict.items():
            assert value is not None


@pytest.mark.property
@pytest.mark.domain
class TestOnboardingStateMachineProperties:
    """Property-based tests for OnboardingStateMachine."""

    @given(initial_state=st.sampled_from(OnboardingState))
    def test_state_machine_progress_percentage_is_bounded(self, initial_state):
        """Test that progress percentage is always between 0 and 100."""
        sm = OnboardingStateMachine(initial_state)
        progress = sm.get_progress_percentage()

        assert 0.0 <= progress <= 100.0

    @given(initial_state=st.sampled_from(OnboardingState))
    def test_state_machine_is_complete_only_at_dashboard(self, initial_state):
        """Test that state machine is complete only at dashboard state."""
        sm = OnboardingStateMachine(initial_state)

        if initial_state == OnboardingState.DASHBOARD:
            assert sm.is_complete
        else:
            assert not sm.is_complete

    def test_state_machine_valid_transition_sequence_always_works(self):
        """Test that the valid transition sequence always works."""
        sm = OnboardingStateMachine()

        # Should be able to complete the full sequence
        assert sm.current_state == OnboardingState.REGISTRATION

        sm.complete_registration()
        assert sm.current_state == OnboardingState.PROFILE_SETUP

        sm.complete_profile_setup()
        assert sm.current_state == OnboardingState.INITIAL_GOALS

        sm.complete_initial_goals()
        assert sm.current_state == OnboardingState.DASHBOARD
        assert sm.is_complete

    def test_state_machine_skip_sequence_always_works(self):
        """Test that skipping to dashboard works from valid states."""
        # From PROFILE_SETUP
        sm = OnboardingStateMachine(OnboardingState.PROFILE_SETUP)
        sm.skip_to_dashboard()
        assert sm.current_state == OnboardingState.DASHBOARD
        assert sm.is_complete

        # From INITIAL_GOALS
        sm = OnboardingStateMachine(OnboardingState.INITIAL_GOALS)
        sm.skip_to_dashboard()
        assert sm.current_state == OnboardingState.DASHBOARD
        assert sm.is_complete
