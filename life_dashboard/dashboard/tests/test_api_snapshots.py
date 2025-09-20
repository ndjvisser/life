"""
Snapshot tests for dashboard API responses - preventing breaking changes.
"""

import json
from datetime import date, datetime

import pytest

pytest.importorskip("pytest_snapshot")

from life_dashboard.dashboard.domain.entities import UserProfile
from life_dashboard.dashboard.domain.state_machines import OnboardingStateMachine
from life_dashboard.dashboard.domain.value_objects import OnboardingState


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
            "full_name": profile.full_name,
            "experience_to_next_level": profile.experience_to_next_level,
            "level_progress_percentage": round(profile.level_progress_percentage, 1),
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-15T14:30:00",
        }

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "user_profile_response.json",
        )

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
            "experience_to_next_level": profile.experience_to_next_level,
            "level_progress_percentage": round(profile.level_progress_percentage, 1),
            "level_up_rewards": {
                "bonus_experience": 0,
                "unlocked_features": [],
                "achievement_unlocked": False,
            },
        }

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "experience_update_response.json",
        )

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

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "onboarding_status_response.json",
        )

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
        profile.update_profile(
            bio="Updated bio with more details about my experience.",
            location="New York, NY",
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
            "full_name": profile.full_name,
            "updated_fields": ["bio", "location"],
            "update_timestamp": "2023-01-15T14:30:00",
            "validation_status": "success",
        }

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "profile_update_response.json",
        )

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

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "onboarding_completion_response.json",
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
                    profile.level_progress_percentage, 1
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

        snapshot.assert_match(
            json.dumps(response_data, indent=2, sort_keys=True),
            "user_statistics_response.json",
        )
