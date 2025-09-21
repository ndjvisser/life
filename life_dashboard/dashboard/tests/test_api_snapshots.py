"""
Snapshot tests for dashboard API responses - preventing breaking changes.
"""

from datetime import date, datetime

import pytest

pytest.importorskip("pytest_snapshot")

from life_dashboard.dashboard.domain.entities import UserProfile
from life_dashboard.dashboard.domain.state_machines import OnboardingStateMachine
from life_dashboard.dashboard.domain.value_objects import OnboardingState
from tests.snapshot_utils import assert_json_snapshot


def resolve_callable(value):
    """Return the result of calling value if callable, else the value itself."""

    return value() if callable(value) else value


@pytest.mark.snapshot
@pytest.mark.unit
class TestDashboardAPISnapshots:
    """Test dashboard API response snapshots."""

    def test_user_profile_response_snapshot(self, snapshot):
        """Test user profile response structure."""
        profile = UserProfile(
            user_id=1,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            bio="Software developer with a passion for learning and building great products.",
            location="San Francisco, CA",
            birth_date=date(1990, 1, 15),
            experience_points=2750,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 14, 30, 0),
        )

        # Create predictable response data
        response_data = {
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
            "full_name": resolve_callable(profile.full_name),
            "experience_to_next_level": resolve_callable(
                profile.experience_to_next_level
            ),
            "level_progress_percentage": round(
                resolve_callable(profile.level_progress_percentage), 1
            ),
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-15T14:30:00",
        }

        assert_json_snapshot(snapshot, response_data, "user_profile_response.json")

    def test_experience_update_response_snapshot(self, snapshot):
        """Test experience update response structure."""
        profile = UserProfile(user_id=1, username="johndoe", experience_points=1800)

        # Add experience that causes level up
        new_level, level_up = profile.add_experience(750)

        # Create predictable response data
        response_data = {
            "new_level": new_level,
            "level_up_occurred": level_up,
            "total_experience": profile.experience_points,
            "experience_to_next_level": resolve_callable(
                profile.experience_to_next_level
            ),
            "level_progress_percentage": round(
                resolve_callable(profile.level_progress_percentage), 1
            ),
            "level_up_rewards": {
                "bonus_experience": 0,
                "unlocked_features": [],
                "achievement_unlocked": False,
            },
        }

        assert_json_snapshot(snapshot, response_data, "experience_update_response.json")

    def test_onboarding_status_response_snapshot(self, snapshot):
        """Test onboarding status response structure."""
        sm = OnboardingStateMachine(OnboardingState.PROFILE_SETUP)

        # Create predictable response data
        response_data = {
            "current_state": sm.current_state.value,
            "is_complete": sm.is_complete,
            "progress_percentage": sm.get_progress_percentage(),
            "next_step": sm.next_step.value if sm.next_step else None,
            "available_actions": ["complete_profile_setup", "skip_to_dashboard"],
            "completion_requirements": {
                "profile_setup": {
                    "required_fields": ["first_name", "last_name"],
                    "optional_fields": ["bio", "location", "birth_date"],
                }
            },
        }

        assert_json_snapshot(snapshot, response_data, "onboarding_status_response.json")

    def test_profile_update_response_snapshot(self, snapshot):
        """Test profile update response structure."""
        profile = UserProfile(
            user_id=1,
            username="johndoe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )

        # Update profile
        update_payload = {
            "bio": "Updated bio with more details about my experience.",
            "location": "New York, NY",
        }
        profile.update_profile(**update_payload)

        full_name_value = resolve_callable(profile.full_name)
        updated_fields = list(update_payload.keys())
        profile.updated_at = datetime(2023, 1, 15, 14, 30, 0)
        update_timestamp = profile.updated_at.isoformat(timespec="seconds")

        # Create predictable response data
        response_data = {
            "user_id": profile.user_id,
            "username": profile.username,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "bio": profile.bio,
            "location": profile.location,
            "full_name": full_name_value,
            "updated_fields": updated_fields,
            "update_timestamp": update_timestamp,
            "validation_status": "success",
        }

        assert_json_snapshot(snapshot, response_data, "profile_update_response.json")

    def test_onboarding_completion_response_snapshot(self, snapshot):
        """Test onboarding completion response structure."""
        sm = OnboardingStateMachine()

        # Complete full onboarding sequence
        sm.complete_registration()
        sm.complete_profile_setup()
        sm.complete_initial_goals()

        # Create predictable response data
        response_data = {
            "current_state": sm.current_state.value,
            "is_complete": sm.is_complete,
            "progress_percentage": sm.get_progress_percentage(),
            "next_step": sm.next_step,
            "completion_timestamp": "2023-01-01T12:00:00",
            "completion_rewards": {
                "welcome_bonus_experience": 100,
                "unlocked_features": [
                    "dashboard_access",
                    "quest_creation",
                    "achievement_tracking",
                    "journal_entries",
                ],
                "welcome_achievement": {
                    "id": "onboarding_complete",
                    "name": "Welcome to LIFE!",
                    "description": "Successfully completed the onboarding process",
                },
            },
            "next_recommended_actions": [
                "create_first_quest",
                "set_initial_goals",
                "explore_dashboard",
            ],
        }

        assert_json_snapshot(
            snapshot, response_data, "onboarding_completion_response.json"
        )

    def test_user_statistics_response_snapshot(self, snapshot):
        """Test user statistics response structure."""
        profile = UserProfile(
            user_id=1,
            username="johndoe",
            experience_points=5750,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
        )

        # Calculate statistics
        days_active = 45
        total_sessions = 120
        avg_session_duration = 25.5  # minutes

        # Create predictable response data
        response_data = {
            "user_profile": {
                "user_id": profile.user_id,
                "username": profile.username,
                "level": profile.level,
                "experience_points": profile.experience_points,
                "level_progress_percentage": round(
                    resolve_callable(profile.level_progress_percentage), 1
                ),
            },
            "activity_statistics": {
                "days_active": days_active,
                "total_sessions": total_sessions,
                "average_session_duration_minutes": avg_session_duration,
                "account_age_days": 45,
                "last_active": "2023-02-15T18:45:00",
            },
            "achievement_statistics": {
                "total_achievements": 12,
                "bronze_achievements": 8,
                "silver_achievements": 3,
                "gold_achievements": 1,
                "platinum_achievements": 0,
                "completion_rate": 75.0,
            },
            "progress_statistics": {
                "quests_completed": 28,
                "habits_maintained": 5,
                "journal_entries": 42,
                "skills_practiced": 7,
            },
        }

        assert_json_snapshot(snapshot, response_data, "user_statistics_response.json")
