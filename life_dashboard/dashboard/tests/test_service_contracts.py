"""
Contract tests for dashboard services - validating service layer APIs with Pydantic.
"""

from datetime import datetime

import pytest
from pydantic import BaseModel, ConfigDict, Field

from life_dashboard.dashboard.domain.entities import UserProfile
from life_dashboard.dashboard.domain.state_machines import OnboardingStateMachine
from life_dashboard.dashboard.domain.value_objects import OnboardingState


# Pydantic contracts for service responses
class UserProfileResponse(BaseModel):
    """Contract for user profile responses."""

    model_config = ConfigDict(extra="forbid")

    user_id: int
    username: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    bio: str = ""
    location: str = ""
    birth_date: str | None = None  # ISO date string
    experience_points: int = Field(ge=0)
    level: int = Field(ge=1)
    full_name: str
    experience_to_next_level: int = Field(ge=0)
    level_progress_percentage: float = Field(ge=0.0, le=100.0)
    created_at: str | None = None
    updated_at: str | None = None


class ExperienceUpdateResponse(BaseModel):
    """Contract for experience update responses."""

    model_config = ConfigDict(extra="forbid")

    new_level: int = Field(ge=1)
    level_up_occurred: bool
    total_experience: int = Field(ge=0)
    experience_to_next_level: int = Field(ge=0)
    level_progress_percentage: float = Field(ge=0.0, le=100.0)


class OnboardingStatusResponse(BaseModel):
    """Contract for onboarding status responses."""

    model_config = ConfigDict(extra="forbid")

    current_state: str
    is_complete: bool
    progress_percentage: float = Field(ge=0.0, le=100.0)
    next_step: str | None = None


class ProfileUpdateRequest(BaseModel):
    """Contract for profile update requests."""

    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(None, max_length=150)
    last_name: str | None = Field(None, max_length=150)
    email: str | None = Field(None, max_length=254)
    bio: str | None = Field(None, max_length=500)
    location: str | None = Field(None, max_length=30)
    birth_date: str | None = None  # ISO date string


class ExperienceUpdateRequest(BaseModel):
    """Contract for experience update requests."""

    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(gt=0)
    experience_points: int = Field(gt=0)
    reason: str | None = None


@pytest.mark.contract
@pytest.mark.unit
class TestDashboardServiceContracts:
    """Test dashboard service contracts."""

    def test_profile_update_request_contract_validation(self):
        """Test profile update request contract validation."""
        # Valid request
        valid_request = ProfileUpdateRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            bio="Software developer with a passion for learning.",
            location="San Francisco, CA",
        )

        assert valid_request.first_name == "John"
        assert valid_request.last_name == "Doe"
        assert valid_request.email == "john.doe@example.com"

        # Invalid request - field too long
        with pytest.raises(ValueError):
            ProfileUpdateRequest(first_name="x" * 151)

        with pytest.raises(ValueError):
            ProfileUpdateRequest(bio="x" * 501)

    def test_experience_update_request_contract_validation(self):
        """Test experience update request contract validation."""
        # Valid request
        valid_request = ExperienceUpdateRequest(
            user_id=1, experience_points=500, reason="Quest completion"
        )

        assert valid_request.user_id == 1
        assert valid_request.experience_points == 500
        assert valid_request.reason == "Quest completion"

        # Invalid request - non-positive user_id
        with pytest.raises(ValueError):
            ExperienceUpdateRequest(user_id=0, experience_points=500)

        # Invalid request - non-positive experience_points
        with pytest.raises(ValueError):
            ExperienceUpdateRequest(user_id=1, experience_points=0)

    def test_user_profile_response_contract(self):
        """Test that UserProfile entity conforms to response contract."""
        profile = UserProfile(
            user_id=1,
            username="testuser",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            bio="Test bio",
            location="Test City",
            experience_points=1500,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Convert to dict format expected by contract
        profile_data = {
            "user_id": profile.user_id,
            "username": profile.username,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "bio": profile.bio,
            "location": profile.location,
            "birth_date": profile.birth_date.isoformat()
            if profile.birth_date
            else None,
            "experience_points": profile.experience_points,
            "level": profile.level,
            "full_name": profile.full_name,
            "experience_to_next_level": profile.experience_to_next_level,
            "level_progress_percentage": profile.level_progress_percentage,
            "created_at": profile.created_at.isoformat()
            if profile.created_at
            else None,
            "updated_at": profile.updated_at.isoformat()
            if profile.updated_at
            else None,
        }

        # Validate against contract
        response = UserProfileResponse(**profile_data)

        assert response.user_id == 1
        assert response.username == "testuser"
        assert response.full_name == "John Doe"
        assert response.experience_points == 1500
        assert response.level == profile.level  # Level calculated from experience
        assert 0.0 <= response.level_progress_percentage <= 100.0

    def test_experience_update_response_contract(self):
        """Test experience update response contract."""
        profile = UserProfile(user_id=1, username="testuser", experience_points=500)

        new_level, level_up = profile.add_experience(1000)

        # Create response data
        response_data = {
            "new_level": new_level,
            "level_up_occurred": level_up,
            "total_experience": profile.experience_points,
            "experience_to_next_level": profile.experience_to_next_level,
            "level_progress_percentage": profile.level_progress_percentage,
        }

        # Validate against contract
        response = ExperienceUpdateResponse(**response_data)

        assert response.new_level == 2
        assert response.level_up_occurred is True
        assert response.total_experience == 1500
        assert response.experience_to_next_level >= 0
        assert 0.0 <= response.level_progress_percentage <= 100.0

    def test_onboarding_status_response_contract(self):
        """Test onboarding status response contract."""
        sm = OnboardingStateMachine(OnboardingState.PROFILE_SETUP)

        # Create response data
        response_data = {
            "current_state": sm.current_state.value,
            "is_complete": sm.is_complete,
            "progress_percentage": sm.get_progress_percentage(),
            "next_step": sm.next_step.value if sm.next_step else None,
        }

        # Validate against contract
        response = OnboardingStatusResponse(**response_data)

        assert response.current_state == "profile_setup"
        assert response.is_complete is False
        assert response.progress_percentage == 33.3
        assert response.next_step == "initial_goals"

    def test_contract_schema_examples_are_valid(self):
        """Test that contract schema examples are valid."""
        # Test UserProfileResponse schema
        example_profile = {
            "user_id": 1,
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "bio": "Software developer",
            "location": "San Francisco",
            "birth_date": "1990-01-01",
            "experience_points": 2500,
            "level": 3,
            "full_name": "John Doe",
            "experience_to_next_level": 500,
            "level_progress_percentage": 50.0,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
        }

        profile_response = UserProfileResponse(**example_profile)
        assert profile_response.user_id == 1
        assert profile_response.full_name == "John Doe"

        # Test ExperienceUpdateResponse schema
        example_experience = {
            "new_level": 3,
            "level_up_occurred": True,
            "total_experience": 2500,
            "experience_to_next_level": 500,
            "level_progress_percentage": 50.0,
        }

        experience_response = ExperienceUpdateResponse(**example_experience)
        assert experience_response.new_level == 3
        assert experience_response.level_up_occurred is True

        # Test OnboardingStatusResponse schema
        example_onboarding = {
            "current_state": "profile_setup",
            "is_complete": False,
            "progress_percentage": 33.3,
            "next_step": "initial_goals",
        }

        onboarding_response = OnboardingStatusResponse(**example_onboarding)
        assert onboarding_response.current_state == "profile_setup"
        assert onboarding_response.is_complete is False
