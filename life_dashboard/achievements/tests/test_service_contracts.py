"""
Contract tests for Achievements domain services using Pydantic models.

These tests validate service layer APIs and ensure consistent interfaces.
"""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

from pydantic import BaseModel

from life_dashboard.achievements.domain.entities import (
    Achievement,
    AchievementCategory,
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
    UserAchievementId,
    UserId,
)


# Pydantic models for API contracts
class AchievementCreateRequest(BaseModel):
    """Contract for achievement creation requests"""

    name: str
    description: str
    tier: str
    category: str
    icon: str = ""
    experience_reward: int
    required_level: int = 1
    required_skill_level: int | None = None
    required_quest_completions: int = 0
    is_hidden: bool = False
    is_repeatable: bool = False

    class Config:
        schema_extra = {
            "example": {
                "name": "First Steps",
                "description": "Complete your first quest",
                "tier": "BRONZE",
                "category": "quest_completion",
                "icon": "trophy",
                "experience_reward": 100,
                "required_level": 1,
                "required_quest_completions": 1,
            }
        }


class AchievementResponse(BaseModel):
    """Contract for achievement responses"""

    achievement_id: int
    name: str
    description: str
    tier: str
    category: str
    icon: str
    experience_reward: int
    required_level: int
    required_skill_level: int | None
    required_quest_completions: int
    is_hidden: bool
    is_repeatable: bool
    tier_multiplier: float
    final_experience_reward: int
    difficulty_rating: str
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "achievement_id": 1,
                "name": "First Steps",
                "description": "Complete your first quest",
                "tier": "BRONZE",
                "category": "quest_completion",
                "icon": "trophy",
                "experience_reward": 100,
                "required_level": 1,
                "required_skill_level": None,
                "required_quest_completions": 1,
                "is_hidden": False,
                "is_repeatable": False,
                "tier_multiplier": 1.0,
                "final_experience_reward": 100,
                "difficulty_rating": "Easy",
                "created_at": "2024-01-01T10:00:00",
            }
        }


class UnlockAchievementRequest(BaseModel):
    """Contract for unlock achievement requests"""

    user_id: int
    achievement_id: int
    notes: str = ""

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "achievement_id": 1,
                "notes": "Great job completing your first quest!",
            }
        }


class UnlockAchievementResponse(BaseModel):
    """Contract for unlock achievement responses"""

    user_achievement_id: int
    user_id: int
    achievement_id: int
    unlocked_at: datetime
    notes: str
    experience_gained: int

    class Config:
        schema_extra = {
            "example": {
                "user_achievement_id": 1,
                "user_id": 1,
                "achievement_id": 1,
                "unlocked_at": "2024-01-15T14:30:00",
                "notes": "Great job completing your first quest!",
                "experience_gained": 100,
            }
        }


class AchievementStatisticsResponse(BaseModel):
    """Contract for achievement statistics responses"""

    total_achievements: int
    unlocked_achievements: int
    completion_percentage: float
    tier_breakdown: dict[str, dict[str, Any]]
    category_breakdown: dict[str, dict[str, Any]]
    recent_achievements_count: int
    total_experience_from_achievements: int
    average_unlock_rate_per_month: float

    class Config:
        schema_extra = {
            "example": {
                "total_achievements": 50,
                "unlocked_achievements": 12,
                "completion_percentage": 24.0,
                "tier_breakdown": {
                    "BRONZE": {"unlocked": 8, "total": 20, "percentage": 40.0},
                    "SILVER": {"unlocked": 3, "total": 15, "percentage": 20.0},
                    "GOLD": {"unlocked": 1, "total": 10, "percentage": 10.0},
                    "PLATINUM": {"unlocked": 0, "total": 5, "percentage": 0.0},
                },
                "category_breakdown": {
                    "progression": {"unlocked": 5, "total": 15, "percentage": 33.33},
                    "quest_completion": {
                        "unlocked": 4,
                        "total": 12,
                        "percentage": 33.33,
                    },
                    "skill_mastery": {"unlocked": 2, "total": 10, "percentage": 20.0},
                    "streak": {"unlocked": 1, "total": 8, "percentage": 12.5},
                },
                "recent_achievements_count": 3,
                "total_experience_from_achievements": 2500,
                "average_unlock_rate_per_month": 2.4,
            }
        }


class TestAchievementServiceContracts:
    """Test AchievementService API contracts"""

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

    def test_create_achievement_contract_validation(self):
        """Test achievement creation request contract validation"""
        # Valid request should pass validation
        valid_request = AchievementCreateRequest(
            name="First Steps",
            description="Complete your first quest",
            tier="BRONZE",
            category="quest_completion",
            icon="trophy",
            experience_reward=100,
            required_quest_completions=1,
        )

        assert valid_request.name == "First Steps"
        assert valid_request.tier == "BRONZE"
        assert valid_request.category == "quest_completion"

    def test_unlock_achievement_contract_validation(self):
        """Test unlock achievement request contract validation"""
        # Valid request should pass validation
        valid_request = UnlockAchievementRequest(
            user_id=1,
            achievement_id=1,
            notes="Great job!",
        )

        assert valid_request.user_id == 1
        assert valid_request.achievement_id == 1
        assert valid_request.notes == "Great job!"

        # Default values should work
        minimal_request = UnlockAchievementRequest(
            user_id=1,
            achievement_id=1,
        )
        assert minimal_request.notes == ""

    def test_achievement_service_create_returns_valid_response(self):
        """Test that achievement service returns valid response contract"""
        # Mock repository to return an achievement
        mock_achievement = Achievement(
            achievement_id=AchievementId(1),
            name=AchievementName("First Steps"),
            description=AchievementDescription("Complete your first quest"),
            tier=AchievementTier.BRONZE,
            category=AchievementCategory.QUEST_COMPLETION,
            icon=AchievementIcon("trophy"),
            experience_reward=ExperienceReward(100),
            required_level=RequiredLevel(1),
            required_quest_completions=RequiredQuestCompletions(1),
            created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        )
        self.mock_achievement_repository.save.return_value = mock_achievement

        # Create achievement through service
        result = self.achievement_service.create_achievement(
            name="First Steps",
            description="Complete your first quest",
            tier="BRONZE",
            category="quest_completion",
            icon="trophy",
            experience_reward=100,
            required_level=1,
            required_quest_completions=1,
        )

        # Validate response can be serialized to contract
        response_data = {
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
            "created_at": result.created_at,
        }

        # Should not raise validation error
        response = AchievementResponse(**response_data)
        assert response.achievement_id == 1
        assert response.name == "First Steps"

    def test_unlock_achievement_returns_valid_response(self):
        """Test that unlock achievement returns valid response contract"""
        # Mock achievement
        mock_achievement = Achievement(
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

        # Mock user achievement
        mock_user_achievement = UserAchievement(
            user_achievement_id=UserAchievementId(1),
            user_id=UserId(1),
            achievement_id=AchievementId(1),
            unlocked_at=datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
            notes="Great job!",
        )

        self.mock_achievement_repository.get_by_id.return_value = mock_achievement
        self.mock_user_achievement_repository.has_achievement.return_value = False
        self.mock_user_achievement_repository.save.return_value = mock_user_achievement

        # Unlock achievement
        result_achievement, experience_gained = (
            self.achievement_service.unlock_achievement(
                UserId(1), AchievementId(1), "Great job!"
            )
        )

        # Validate response contract
        response_data = {
            "user_achievement_id": result_achievement.user_achievement_id.value,
            "user_id": result_achievement.user_id.value,
            "achievement_id": result_achievement.achievement_id.value,
            "unlocked_at": result_achievement.unlocked_at,
            "notes": result_achievement.notes,
            "experience_gained": experience_gained,
        }

        unlock_response = UnlockAchievementResponse(**response_data)
        assert unlock_response.experience_gained == 100
        assert unlock_response.user_id == 1

    def test_achievement_statistics_returns_valid_response(self):
        """Test that achievement statistics returns valid response contract"""
        # Mock data
        mock_achievements = [
            Achievement(
                achievement_id=AchievementId(1),
                name=AchievementName("Bronze Achievement"),
                description=AchievementDescription("Bronze test"),
                tier=AchievementTier.BRONZE,
                category=AchievementCategory.PROGRESSION,
                icon=AchievementIcon("BRONZE"),
                experience_reward=ExperienceReward(100),
                required_level=RequiredLevel(5),
            ),
            Achievement(
                achievement_id=AchievementId(2),
                name=AchievementName("Silver Achievement"),
                description=AchievementDescription("Silver test"),
                tier=AchievementTier.SILVER,
                category=AchievementCategory.QUEST_COMPLETION,
                icon=AchievementIcon("SILVER"),
                experience_reward=ExperienceReward(200),
                required_level=RequiredLevel(10),
            ),
        ]

        mock_user_achievements = [
            UserAchievement(
                user_achievement_id=UserAchievementId(1),
                user_id=UserId(1),
                achievement_id=AchievementId(1),
                unlocked_at=datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
            ),
        ]

        self.mock_achievement_repository.get_all_achievements.return_value = (
            mock_achievements
        )
        self.mock_user_achievement_repository.get_user_achievements.return_value = (
            mock_user_achievements
        )
        self.mock_user_achievement_repository.get_recent_achievements.return_value = (
            mock_user_achievements
        )
        self.mock_achievement_repository.get_by_id.return_value = mock_achievements[0]

        # Get statistics
        stats = self.achievement_service.get_achievement_statistics(UserId(1))

        # Validate response contract
        stats_response = AchievementStatisticsResponse(**stats)
        assert stats_response.total_achievements == 2
        assert stats_response.unlocked_achievements == 1
        assert stats_response.completion_percentage == 50.0

    def test_contract_schema_examples_are_valid(self):
        """Test that all contract schema examples are valid"""
        # Test AchievementCreateRequest example
        achievement_example = AchievementCreateRequest.Config.schema_extra["example"]
        achievement_request = AchievementCreateRequest(**achievement_example)
        assert achievement_request.name == "First Steps"

        # Test UnlockAchievementRequest example
        unlock_example = UnlockAchievementRequest.Config.schema_extra["example"]
        unlock_request = UnlockAchievementRequest(**unlock_example)
        assert unlock_request.user_id == 1
