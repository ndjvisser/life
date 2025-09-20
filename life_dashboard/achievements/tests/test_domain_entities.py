"""
Fast unit tests for Achievements domain entities.

These tests run without Django and focus on pure business logic validation.
"""

from datetime import datetime, timedelta, timezone

import pytest

from life_dashboard.achievements.domain.entities import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
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


class TestAchievement:
    """Test Achievement domain entity"""

    def test_achievement_creation_with_valid_data(self):
        """Test creating an achievement with valid data"""
        achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("First Steps"),
            description=AchievementDescription("Complete your first quest"),
            tier=AchievementTier.BRONZE,
            category=AchievementCategory.QUEST_COMPLETION,
            icon=AchievementIcon("trophy"),
            experience_reward=ExperienceReward(100),
            required_level=RequiredLevel(1),
            required_quest_completions=RequiredQuestCompletions(1),
        )

        assert achievement.achievement_id.value == 1
        assert achievement.name.value == "First Steps"
        assert achievement.tier == AchievementTier.BRONZE
        assert achievement.category == AchievementCategory.QUEST_COMPLETION

    def test_achievement_requires_at_least_one_requirement(self):
        """Test that achievement must have at least one requirement"""
        with pytest.raises(
            ValueError, match="Achievement must have at least one requirement"
        ):
            Achievement(
                achievement_id=AchievementId(1),
                name=AchievementName("Invalid Achievement"),
                description=AchievementDescription("No requirements"),
                tier=AchievementTier.BRONZE,
                category=AchievementCategory.PROGRESSION,
                icon=AchievementIcon("trophy"),
                experience_reward=ExperienceReward(100),
                required_level=RequiredLevel(
                    1
                ),  # This is default, not a real requirement
                required_quest_completions=RequiredQuestCompletions(
                    0
                ),  # No requirement
            )

    def test_achievement_tier_multiplier(self):
        """Test achievement tier experience multipliers"""
        bronze_achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Bronze Achievement"),
            description=AchievementDescription("Bronze tier test"),
            tier=AchievementTier.BRONZE,
            category=AchievementCategory.PROGRESSION,
            icon=AchievementIcon("BRONZE"),
            experience_reward=ExperienceReward(100),
            required_level=RequiredLevel(5),
        )

        platinum_achievement = Achievement(
            achievement_id=AchievementId(2),
            name=AchievementName("Platinum Achievement"),
            description=AchievementDescription("Platinum tier test"),
            tier=AchievementTier.PLATINUM,
            category=AchievementCategory.PROGRESSION,
            icon=AchievementIcon("PLATINUM"),
            experience_reward=ExperienceReward(100),
            required_level=RequiredLevel(50),
        )

        assert bronze_achievement.get_tier_multiplier() == 1.0
        assert bronze_achievement.calculate_final_experience_reward() == 100

        assert platinum_achievement.get_tier_multiplier() == 3.0
        assert platinum_achievement.calculate_final_experience_reward() == 300

    def test_achievement_difficulty_rating(self):
        """Test achievement difficulty rating calculation"""
        # Easy achievement
        easy_achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Easy Achievement"),
            description=AchievementDescription("Easy to get"),
            tier=AchievementTier.BRONZE,
            category=AchievementCategory.PROGRESSION,
            icon=AchievementIcon("easy"),
            experience_reward=ExperienceReward(50),
            required_level=RequiredLevel(5),
        )

        # Legendary achievement
        legendary_achievement = Achievement(
            achievement_id=AchievementId(2),
            name=AchievementName("Legendary Achievement"),
            description=AchievementDescription("Extremely difficult"),
            tier=AchievementTier.PLATINUM,
            category=AchievementCategory.SKILL_MASTERY,
            icon=AchievementIcon("legendary"),
            experience_reward=ExperienceReward(5000),
            required_level=RequiredLevel(80),
            required_skill_level=RequiredSkillLevel(90),
            required_quest_completions=RequiredQuestCompletions(200),
        )

        assert easy_achievement.get_difficulty_rating() == "Easy"
        assert legendary_achievement.get_difficulty_rating() == "Legendary"

    def test_achievement_eligibility_check(self):
        """Test achievement eligibility checking"""
        achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Multi-Requirement Achievement"),
            description=AchievementDescription("Requires multiple things"),
            tier=AchievementTier.SILVER,
            category=AchievementCategory.MILESTONE,
            icon=AchievementIcon("milestone"),
            experience_reward=ExperienceReward(500),
            required_level=RequiredLevel(10),
            required_skill_level=RequiredSkillLevel(25),
            required_quest_completions=RequiredQuestCompletions(5),
        )

        # User meets all requirements
        eligible_user_stats = {
            "level": 15,
            "max_skill_level": 30,
            "quest_completions": 8,
        }
        assert achievement.check_eligibility(eligible_user_stats)

        # User doesn't meet level requirement
        ineligible_user_stats = {
            "level": 8,
            "max_skill_level": 30,
            "quest_completions": 8,
        }
        assert not achievement.check_eligibility(ineligible_user_stats)

    def test_achievement_progress_percentage(self):
        """Test achievement progress percentage calculation"""
        achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Progress Test"),
            description=AchievementDescription("Test progress calculation"),
            tier=AchievementTier.GOLD,
            category=AchievementCategory.PROGRESSION,
            icon=AchievementIcon("progress"),
            experience_reward=ExperienceReward(1000),
            required_level=RequiredLevel(20),
            required_quest_completions=RequiredQuestCompletions(10),
        )

        # 50% progress on both requirements
        user_stats = {
            "level": 10,  # 50% of 20
            "quest_completions": 5,  # 50% of 10
        }

        progress = achievement.get_progress_percentage(user_stats)
        assert progress == 50.0

    def test_achievement_missing_requirements(self):
        """Test missing requirements identification"""
        achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("Requirements Test"),
            description=AchievementDescription("Test missing requirements"),
            tier=AchievementTier.SILVER,
            category=AchievementCategory.SKILL_MASTERY,
            icon=AchievementIcon("skill"),
            experience_reward=ExperienceReward(750),
            required_level=RequiredLevel(15),
            required_skill_level=RequiredSkillLevel(30),
            required_quest_completions=RequiredQuestCompletions(8),
        )

        user_stats = {
            "level": 12,  # Below required 15
            "max_skill_level": 25,  # Below required 30
            "quest_completions": 10,  # Above required 8
        }

        missing = achievement.get_missing_requirements(user_stats)

        assert len(missing) == 2
        assert any("level 15" in req for req in missing)
        assert any("skill level 30" in req for req in missing)
        assert not any("quest" in req for req in missing)  # Quest requirement is met


class TestUserAchievement:
    """Test UserAchievement domain entity"""

    def test_user_achievement_creation_with_valid_data(self):
        """Test creating a user achievement with valid data"""
        user_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            notes="Great job completing your first quest!",
        )

        assert user_achievement.user_achievement_id.value == 1
        assert user_achievement.user_id.value == 1
        assert user_achievement.achievement_id.value == 1
        assert user_achievement.notes == "Great job completing your first quest!"

    def test_user_achievement_notes_validation(self):
        """Test user achievement notes length validation"""
        with pytest.raises(
            ValueError, match="Achievement notes cannot exceed 1000 characters"
        ):
            UserAchievement(
                user_achievement_id=UserAchievementId(1),
                user_id=UserId(1),
                achievement_id=AchievementId(1),
                unlocked_at=datetime.now(timezone.utc),
                notes="x" * 1001,  # Too long
            )

    def test_user_achievement_unlock_age_calculation(self):
        """Test unlock age calculation"""
        # Achievement unlocked 5 days ago
        unlock_date = datetime.now(timezone.utc) - timedelta(days=5)
        user_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=unlock_date,
        )

        age_days = user_achievement.get_unlock_age_days()
        assert age_days == 5

    def test_user_achievement_recent_unlock_check(self):
        """Test recent unlock detection"""
        # Recent achievement (3 days ago)
        recent_unlock = datetime.now(timezone.utc) - timedelta(days=3)
        recent_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=recent_unlock,
        )

        # Old achievement (30 days ago)
        old_unlock = datetime.now(timezone.utc) - timedelta(days=30)
        old_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(2),
            user_id=UserId(1),
            achievement_id=AchievementId(2),
            unlocked_at=old_unlock,
        )

        assert recent_achievement.is_recent_unlock(7)
        assert not old_achievement.is_recent_unlock(7)

    def test_user_achievement_context_management(self):
        """Test unlock context management"""
        user_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=datetime.now(timezone.utc),
        )

        # Add context
        user_achievement.add_context("trigger_quest", "Complete Python Tutorial")
        user_achievement.add_context("user_level", 15)

        assert (
            user_achievement.unlock_context["trigger_quest"]
            == "Complete Python Tutorial"
        )
        assert user_achievement.unlock_context["user_level"] == 15


class TestAchievementProgress:
    """Test AchievementProgress domain entity"""

    def test_achievement_progress_creation_with_valid_data(self):
        """Test creating achievement progress with valid data"""
        progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            progress_percentage=75.5,
            last_updated=datetime.now(timezone.utc),
            missing_requirements=["Reach level 20 (currently 15)"],
            is_eligible=False,
        )

        assert progress.user_id.value == 1
        assert progress.achievement_id.value == 1
        assert progress.progress_percentage == 75.5
        assert not progress.is_eligible

    def test_achievement_progress_percentage_validation(self):
        """Test progress percentage validation"""
        # Invalid percentage (negative)
        with pytest.raises(
            ValueError, match="Progress percentage must be between 0 and 100"
        ):
            AchievementProgress(
                user_id=UserId(1),
                achievement_id=AchievementId(1),
                progress_percentage=-5.0,
                last_updated=datetime.now(timezone.utc),
            )

        # Invalid percentage (over 100)
        with pytest.raises(
            ValueError, match="Progress percentage must be between 0 and 100"
        ):
            AchievementProgress(
                user_id=UserId(1),
                achievement_id=AchievementId(1),
                progress_percentage=105.0,
                last_updated=datetime.now(timezone.utc),
            )

    def test_achievement_progress_update(self):
        """Test progress update functionality"""
        progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            progress_percentage=50.0,
            last_updated=datetime.now(timezone.utc) - timedelta(hours=1),
            missing_requirements=["Reach level 20 (currently 10)"],
            is_eligible=False,
        )

        original_update_time = progress.last_updated

        # Update progress
        progress.update_progress(
            new_percentage=80.0,
            missing_reqs=["Reach level 20 (currently 16)"],
            eligible=False,
        )

        assert progress.progress_percentage == 80.0
        assert progress.missing_requirements == ["Reach level 20 (currently 16)"]
        assert progress.last_updated > original_update_time

    def test_achievement_progress_close_to_completion(self):
        """Test close to completion detection"""
        # Close to completion
        close_progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            progress_percentage=85.0,
            last_updated=datetime.now(timezone.utc),
        )

        # Not close to completion
        far_progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(2),
            progress_percentage=45.0,
            last_updated=datetime.now(timezone.utc),
        )

        assert close_progress.is_close_to_completion(80.0)
        assert not far_progress.is_close_to_completion(80.0)

    def test_achievement_progress_completion_estimates(self):
        """Test completion estimate messages"""
        # Ready to unlock
        ready_progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            progress_percentage=100.0,
            last_updated=datetime.now(timezone.utc),
            is_eligible=True,
        )

        # Almost there
        almost_progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(2),
            progress_percentage=95.0,
            last_updated=datetime.now(timezone.utc),
            is_eligible=False,
        )

        # Just getting started
        starting_progress = AchievementProgress(
            user_id=UserId(1),
            achievement_id=AchievementId(3),
            progress_percentage=15.0,
            last_updated=datetime.now(timezone.utc),
            is_eligible=False,
        )

        assert ready_progress.get_completion_estimate() == "Ready to unlock!"
        assert almost_progress.get_completion_estimate() == "Almost there!"
        assert starting_progress.get_completion_estimate() == "Just getting started"
