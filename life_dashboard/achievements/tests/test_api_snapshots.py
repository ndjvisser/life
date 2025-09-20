"""
Snapshot tests for Achievements API responses.

These tests capture API response structures to prevent breaking changes.
"""

import json
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

pytest.importorskip("pytest_snapshot")
pytest.importorskip("freezegun")
from freezegun import freeze_time

from life_dashboard.achievements.domain.entities import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
from life_dashboard.achievements.domain.services import AchievementService
from life_dashboard.achievements.domain.value_objects import (
    AchievementDescription,
    AchievementIcon,
    AchievementId,
    AchievementName,
    ExperienceReward,
    RequiredLevel,
    RequiredQuestCompletions,
    RequiredSkillLevel,
    UserAchievementId,
    UserId,
)


class TestAchievementAPISnapshots:
    """Snapshot tests for Achievement API responses"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_achievement_repository = Mock()
        self.mock_user_achievement_repository = Mock()
        self.mock_progress_repository = Mock()
        self.achievement_service = AchievementService(
            self.mock_achievement_repository,
            self.mock_user_achievement_repository,
            self.mock_progress_repository,
        )

    def test_achievement_creation_response_snapshot(self, snapshot):
        """Test achievement creation API response structure"""
        # Mock repository response
        mock_achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Master of Skills"),
            description=AchievementDescription(
                "Reach level 50 in any skill and complete 25 quests to demonstrate mastery"
            ),
            tier=AchievementTier.GOLD,
            category=AchievementCategory.SKILL_MASTERY,
            icon=AchievementIcon("master-crown"),
            experience_reward=ExperienceReward(2500),
            required_level=RequiredLevel(25),
            required_skill_level=RequiredSkillLevel(50),
            required_quest_completions=RequiredQuestCompletions(25),
            is_hidden=False,
            is_repeatable=False,
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        )
        self.mock_achievement_repository.save.return_value = mock_achievement

        # Create achievement through service
        result = self.achievement_service.create_achievement(
            name="Master of Skills",
            description="Reach level 50 in any skill and complete 25 quests to demonstrate mastery",
            tier="GOLD",
            category="skill_mastery",
            icon="master-crown",
            experience_reward=2500,
            required_level=25,
            required_skill_level=50,
            required_quest_completions=25,
        )

        # Convert to API response format
        api_response = {
            "achievement_id": result.achievement_id.value,
            "name": result.name.value,
            "description": result.description.value,
            "tier": result.tier.value,
            "category": result.category.value,
            "icon": result.icon.value,
            "experience_reward": result.experience_reward.value,
            "required_level": result.required_level.value,
            "required_skill_level": result.required_skill_level.value
            if result.required_skill_level
            else None,
            "required_quest_completions": result.required_quest_completions.value,
            "is_hidden": result.is_hidden,
            "is_repeatable": result.is_repeatable,
            "tier_multiplier": result.get_tier_multiplier(),
            "final_experience_reward": result.calculate_final_experience_reward(),
            "difficulty_rating": result.get_difficulty_rating(),
            "created_at": result.created_at.isoformat(),
        }

        # Snapshot the response structure
        snapshot.assert_match(
            json.dumps(api_response, indent=2, sort_keys=True),
            "achievement_creation_response.json",
        )

    @freeze_time("2024-01-15 14:30:00", tz_offset=0)
    def test_unlock_achievement_response_snapshot(self, snapshot):
        """Test unlock achievement API response structure"""
        # Mock achievement
        mock_achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("First Steps"),
            description=AchievementDescription("Complete your very first quest"),
            tier=AchievementTier.BRONZE,
            category=AchievementCategory.QUEST_COMPLETION,
            icon=AchievementIcon("first-trophy"),
            experience_reward=ExperienceReward(100),
            required_level=RequiredLevel(1),
            required_quest_completions=RequiredQuestCompletions(1),
        )

        # Mock user achievement with current time
        current_time = datetime.now(timezone.utc)
        mock_user_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=current_time,
            notes="Congratulations on completing your first quest! This is just the beginning of your journey.",
            unlock_context={
                "trigger_quest": "Learn Python Basics",
                "user_level": 2,
                "auto_unlock": True,
            },
        )

        self.mock_achievement_repository.get_by_id.return_value = mock_achievement
        self.mock_user_achievement_repository.has_achievement.return_value = False
        self.mock_user_achievement_repository.save.return_value = mock_user_achievement

        # Unlock achievement
        result_achievement, experience_gained = (
            self.achievement_service.unlock_achievement(
                UserId(1),
                AchievementId(1),
                "Congratulations on completing your first quest! This is just the beginning of your journey.",
            )
        )

        # Convert to API response format
        api_response = {
            "user_achievement": {
                "user_achievement_id": result_achievement.user_achievement_id.value,
                "user_id": result_achievement.user_id.value,
                "achievement_id": result_achievement.achievement_id.value,
                "unlocked_at": result_achievement.unlocked_at.isoformat(),
                "notes": result_achievement.notes,
                "unlock_context": result_achievement.unlock_context,
                "unlock_age_days": result_achievement.get_unlock_age_days(),
                "is_recent_unlock": result_achievement.is_recent_unlock(7),
            },
            "achievement_details": {
                "name": mock_achievement.name.value,
                "description": mock_achievement.description.value,
                "tier": mock_achievement.tier.value,
                "category": mock_achievement.category.value,
                "icon": mock_achievement.icon.value,
                "difficulty_rating": mock_achievement.get_difficulty_rating(),
            },
            "experience_gained": experience_gained,
            "tier_multiplier": mock_achievement.get_tier_multiplier(),
            "unlock_timestamp": result_achievement.unlocked_at.isoformat(),
        }

        # Snapshot the response structure
        snapshot.assert_match(
            json.dumps(api_response, indent=2, sort_keys=True),
            "unlock_achievement_response.json",
        )

    def test_achievement_statistics_response_snapshot(self, snapshot):
        """Test achievement statistics API response structure"""
        # Mock diverse achievements
        mock_achievements = [
            Achievement(
                achievement_id=AchievementId(1),
                name=AchievementName("First Steps"),
                description=AchievementDescription("Complete first quest"),
                tier=AchievementTier.BRONZE,
                category=AchievementCategory.QUEST_COMPLETION,
                icon=AchievementIcon("bronze-trophy"),
                experience_reward=ExperienceReward(100),
                required_level=RequiredLevel(1),
                required_quest_completions=RequiredQuestCompletions(1),
            ),
            Achievement(
                achievement_id=AchievementId(2),
                name=AchievementName("Skill Apprentice"),
                description=AchievementDescription("Reach level 25 in any skill"),
                tier=AchievementTier.SILVER,
                category=AchievementCategory.SKILL_MASTERY,
                icon=AchievementIcon("silver-star"),
                experience_reward=ExperienceReward(500),
                required_level=RequiredLevel(10),
                required_skill_level=RequiredSkillLevel(25),
            ),
            Achievement(
                achievement_id=AchievementId(3),
                name=AchievementName("Quest Master"),
                description=AchievementDescription("Complete 50 quests"),
                tier=AchievementTier.GOLD,
                category=AchievementCategory.QUEST_COMPLETION,
                icon=AchievementIcon("gold-crown"),
                experience_reward=ExperienceReward(1500),
                required_level=RequiredLevel(20),
                required_quest_completions=RequiredQuestCompletions(50),
            ),
            Achievement(
                achievement_id=AchievementId(4),
                name=AchievementName("Legendary Master"),
                description=AchievementDescription(
                    "Reach level 80 and master 3 skills"
                ),
                tier=AchievementTier.PLATINUM,
                category=AchievementCategory.MILESTONE,
                icon=AchievementIcon("platinum-diamond"),
                experience_reward=ExperienceReward(5000),
                required_level=RequiredLevel(80),
                required_skill_level=RequiredSkillLevel(90),
                required_quest_completions=RequiredQuestCompletions(100),
            ),
        ]

        # Mock user achievements (user has unlocked 2 out of 4)
        mock_user_achievements = [
            UserAchievement(
                user_achievement_id=UserAchievementId(1),
                user_id=UserId(1),
                achievement_id=AchievementId(1),
                unlocked_at=datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
            ),
            UserAchievement(
                user_achievement_id=UserAchievementId(2),
                user_id=UserId(1),
                achievement_id=AchievementId(2),
                unlocked_at=datetime(2024, 1, 20, 16, 45, 0, tzinfo=timezone.utc),
            ),
        ]

        # Setup mocks
        self.mock_achievement_repository.get_all_achievements.return_value = (
            mock_achievements
        )
        self.mock_user_achievement_repository.get_user_achievements.return_value = (
            mock_user_achievements
        )
        self.mock_user_achievement_repository.get_recent_achievements.return_value = (
            mock_user_achievements[-1:]
        )

        # Mock get_by_id to return appropriate achievements
        def mock_get_by_id(achievement_id):
            return next(
                (a for a in mock_achievements if a.achievement_id == achievement_id),
                None,
            )

        self.mock_achievement_repository.get_by_id.side_effect = mock_get_by_id

        # Get statistics
        stats = self.achievement_service.get_achievement_statistics(UserId(1))

        # Convert to API response format
        api_response = {
            "user_id": 1,
            "statistics_generated_at": datetime(
                2024, 1, 25, 18, 0, 0, tzinfo=timezone.utc
            ).isoformat(),
            "achievement_statistics": stats,
            "progress_insights": {
                "completion_level": "Getting Started"
                if stats["completion_percentage"] < 25
                else "Making Progress",
                "strongest_category": max(
                    stats["category_breakdown"].items(),
                    key=lambda x: x[1]["percentage"],
                )[0],
                "next_tier_focus": "SILVER",  # Based on current progress
                "achievements_this_month": stats["recent_achievements_count"],
            },
            "recommendations": [
                "Focus on quest completion to unlock more bronze achievements",
                "Work on skill development to unlock silver tier achievements",
                "You're making great progress - keep it up!",
            ],
        }

        # Snapshot the response structure
        snapshot.assert_match(
            json.dumps(api_response, indent=2, sort_keys=True),
            "achievement_statistics_response.json",
        )

    def test_achievement_progress_response_snapshot(self, snapshot):
        """Test achievement progress API response structure"""
        # Mock achievement progress data
        mock_progress_list = [
            AchievementProgress(
                user_id=UserId(1),
                achievement_id=AchievementId(3),
                progress_percentage=75.0,
                last_updated=datetime(2024, 1, 25, 12, 0, 0, tzinfo=timezone.utc),
                missing_requirements=["Complete 13 more quests (currently 37/50)"],
                is_eligible=False,
            ),
            AchievementProgress(
                user_id=UserId(1),
                achievement_id=AchievementId(4),
                progress_percentage=45.0,
                last_updated=datetime(2024, 1, 25, 12, 0, 0, tzinfo=timezone.utc),
                missing_requirements=[
                    "Reach level 80 (currently 35)",
                    "Reach skill level 90 (currently 60)",
                    "Complete 65 more quests (currently 35/100)",
                ],
                is_eligible=False,
            ),
        ]

        # Mock achievements for details
        mock_achievements = {
            3: Achievement(
                achievement_id=AchievementId(3),
                name=AchievementName("Quest Master"),
                description=AchievementDescription("Complete 50 quests"),
                tier=AchievementTier.GOLD,
                category=AchievementCategory.QUEST_COMPLETION,
                icon=AchievementIcon("gold-crown"),
                experience_reward=ExperienceReward(1500),
                required_level=RequiredLevel(20),
                required_quest_completions=RequiredQuestCompletions(50),
            ),
            4: Achievement(
                achievement_id=AchievementId(4),
                name=AchievementName("Legendary Master"),
                description=AchievementDescription(
                    "Reach level 80 and master 3 skills"
                ),
                tier=AchievementTier.PLATINUM,
                category=AchievementCategory.MILESTONE,
                icon=AchievementIcon("platinum-diamond"),
                experience_reward=ExperienceReward(5000),
                required_level=RequiredLevel(80),
                required_skill_level=RequiredSkillLevel(90),
                required_quest_completions=RequiredQuestCompletions(100),
            ),
        }

        # Convert to API response format
        api_response = {
            "user_id": 1,
            "progress_updated_at": datetime(
                2024, 1, 25, 12, 0, 0, tzinfo=timezone.utc
            ).isoformat(),
            "achievement_progress": [
                {
                    "achievement_id": progress.achievement_id.value,
                    "achievement_name": mock_achievements[
                        progress.achievement_id.value
                    ].name.value,
                    "achievement_tier": mock_achievements[
                        progress.achievement_id.value
                    ].tier.value,
                    "achievement_category": mock_achievements[
                        progress.achievement_id.value
                    ].category.value,
                    "progress_percentage": progress.progress_percentage,
                    "missing_requirements": progress.missing_requirements,
                    "is_eligible": progress.is_eligible,
                    "is_close_to_completion": progress.is_close_to_completion(70.0),
                    "completion_estimate": progress.get_completion_estimate(),
                    "last_updated": progress.last_updated.isoformat(),
                    "potential_experience_reward": mock_achievements[
                        progress.achievement_id.value
                    ].calculate_final_experience_reward(),
                }
                for progress in mock_progress_list
            ],
            "summary": {
                "total_tracked": len(mock_progress_list),
                "close_to_completion": len(
                    [p for p in mock_progress_list if p.is_close_to_completion(70.0)]
                ),
                "eligible_to_unlock": len(
                    [p for p in mock_progress_list if p.is_eligible]
                ),
                "average_progress": sum(
                    p.progress_percentage for p in mock_progress_list
                )
                / len(mock_progress_list),
            },
        }

        # Snapshot the response structure
        snapshot.assert_match(
            json.dumps(api_response, indent=2, sort_keys=True),
            "achievement_progress_response.json",
        )
