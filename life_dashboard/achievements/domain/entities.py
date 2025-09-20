"""
Achievements Domain Entities

Pure Python domain objects representing core achievements business concepts.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .value_objects import (
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


class AchievementTier(Enum):
    """Achievement tier enumeration"""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class AchievementCategory(Enum):
    """Achievement category enumeration"""

    PROGRESSION = "progression"  # Level-based achievements
    SKILL_MASTERY = "skill_mastery"  # Skill-based achievements
    QUEST_COMPLETION = "quest_completion"  # Quest-based achievements
    STREAK = "streak"  # Streak-based achievements
    MILESTONE = "milestone"  # Special milestone achievements
    SOCIAL = "social"  # Social achievements
    EXPLORATION = "exploration"  # Discovery achievements


@dataclass
class Achievement:
    """
    Achievement domain entity representing an unlockable achievement.

    Contains pure business logic for achievement requirements, validation,
    and reward calculation.
    """

    achievement_id: AchievementId
    name: AchievementName
    description: AchievementDescription
    tier: AchievementTier
    category: AchievementCategory
    icon: AchievementIcon
    experience_reward: ExperienceReward
    required_level: RequiredLevel
    required_skill_level: RequiredSkillLevel | None = None
    required_quest_completions: RequiredQuestCompletions = field(
        default_factory=lambda: RequiredQuestCompletions(0)
    )
    is_hidden: bool = False  # Hidden until unlocked
    is_repeatable: bool = False  # Can be unlocked multiple times
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate achievement data after initialization"""
        self._validate_requirements()

    def _validate_requirements(self):
        """Validate achievement requirements are consistent"""
        # Ensure at least one requirement is specified
        has_level_req = self.required_level.value > 1
        has_skill_req = self.required_skill_level is not None
        has_quest_req = self.required_quest_completions.value > 0

        if not (has_level_req or has_skill_req or has_quest_req):
            raise ValueError("Achievement must have at least one requirement")

    def get_tier_multiplier(self) -> float:
        """Get experience multiplier based on achievement tier"""
        multipliers = {
            AchievementTier.BRONZE: 1.0,
            AchievementTier.SILVER: 1.5,
            AchievementTier.GOLD: 2.0,
            AchievementTier.PLATINUM: 3.0,
        }
        return multipliers[self.tier]

    def calculate_final_experience_reward(self) -> int:
        """Calculate final experience reward with tier multiplier"""
        base_reward = self.experience_reward.value
        multiplier = self.get_tier_multiplier()
        return int(base_reward * multiplier)

    def get_difficulty_rating(self) -> str:
        """Get difficulty rating based on requirements and tier"""
        difficulty_score = 0

        # Level requirement difficulty
        if self.required_level.value >= 50:
            difficulty_score += 3
        elif self.required_level.value >= 25:
            difficulty_score += 2
        elif self.required_level.value >= 10:
            difficulty_score += 1

        # Skill requirement difficulty
        if self.required_skill_level:
            if self.required_skill_level.value >= 80:
                difficulty_score += 3
            elif self.required_skill_level.value >= 50:
                difficulty_score += 2
            elif self.required_skill_level.value >= 25:
                difficulty_score += 1

        # Quest requirement difficulty
        if self.required_quest_completions.value >= 100:
            difficulty_score += 3
        elif self.required_quest_completions.value >= 50:
            difficulty_score += 2
        elif self.required_quest_completions.value >= 10:
            difficulty_score += 1

        # Tier difficulty
        tier_difficulty = {
            AchievementTier.BRONZE: 0,
            AchievementTier.SILVER: 1,
            AchievementTier.GOLD: 2,
            AchievementTier.PLATINUM: 3,
        }
        difficulty_score += tier_difficulty[self.tier]

        # Convert to rating
        if difficulty_score >= 8:
            return "Legendary"
        elif difficulty_score >= 6:
            return "Very Hard"
        elif difficulty_score >= 4:
            return "Hard"
        elif difficulty_score >= 2:
            return "Medium"
        else:
            return "Easy"

    def check_eligibility(self, user_stats: dict[str, Any]) -> bool:
        """Check if user meets requirements for this achievement"""
        # Check level requirement
        user_level = user_stats.get("level", 1)
        if user_level < self.required_level.value:
            return False

        # Check skill level requirement
        if self.required_skill_level:
            max_skill_level = user_stats.get("max_skill_level", 1)
            if max_skill_level < self.required_skill_level.value:
                return False

        # Check quest completions requirement
        quest_completions = user_stats.get("quest_completions", 0)
        if quest_completions < self.required_quest_completions.value:
            return False

        return True

    def get_progress_percentage(self, user_stats: dict[str, Any]) -> float:
        """Calculate progress percentage towards this achievement"""
        total_requirements = 0
        met_requirements = 0

        # Level requirement progress
        user_level = user_stats.get("level", 1)
        level_progress = min(user_level / self.required_level.value, 1.0)
        total_requirements += 1
        met_requirements += level_progress

        # Skill level requirement progress
        if self.required_skill_level:
            max_skill_level = user_stats.get("max_skill_level", 1)
            skill_progress = min(max_skill_level / self.required_skill_level.value, 1.0)
            total_requirements += 1
            met_requirements += skill_progress

        # Quest completions requirement progress
        if self.required_quest_completions.value > 0:
            quest_completions = user_stats.get("quest_completions", 0)
            quest_progress = min(
                quest_completions / self.required_quest_completions.value, 1.0
            )
            total_requirements += 1
            met_requirements += quest_progress

        return (
            (met_requirements / total_requirements) * 100
            if total_requirements > 0
            else 100.0
        )

    def get_missing_requirements(self, user_stats: dict[str, Any]) -> list[str]:
        """Get list of missing requirements for this achievement"""
        missing = []

        # Check level requirement
        user_level = user_stats.get("level", 1)
        if user_level < self.required_level.value:
            missing.append(
                f"Reach level {self.required_level.value} (currently {user_level})"
            )

        # Check skill level requirement
        if self.required_skill_level:
            max_skill_level = user_stats.get("max_skill_level", 1)
            if max_skill_level < self.required_skill_level.value:
                missing.append(
                    f"Reach skill level {self.required_skill_level.value} (currently {max_skill_level})"
                )

        # Check quest completions requirement
        if self.required_quest_completions.value > 0:
            quest_completions = user_stats.get("quest_completions", 0)
            if quest_completions < self.required_quest_completions.value:
                missing.append(
                    f"Complete {self.required_quest_completions.value} quests (currently {quest_completions})"
                )

        return missing


@dataclass
class UserAchievement:
    """
    User achievement domain entity representing an unlocked achievement.

    Contains pure business logic for achievement unlocking and tracking.
    """

    user_achievement_id: UserAchievementId
    user_id: UserId
    achievement_id: AchievementId
    unlocked_at: datetime
    notes: str = ""
    unlock_context: dict[str, Any] = field(
        default_factory=dict
    )  # Context when unlocked

    def __post_init__(self):
        """Validate user achievement data after initialization"""
        if len(self.notes) > 1000:
            raise ValueError("Achievement notes cannot exceed 1000 characters")

    def get_unlock_age_days(self) -> int:
        """Get number of days since achievement was unlocked"""
        return (datetime.utcnow() - self.unlocked_at).days

    def is_recent_unlock(self, days_threshold: int = 7) -> bool:
        """Check if achievement was unlocked recently"""
        return self.get_unlock_age_days() <= days_threshold

    def add_context(self, key: str, value: Any) -> None:
        """Add context information about the unlock"""
        self.unlock_context[key] = value


@dataclass
class AchievementProgress:
    """
    Achievement progress tracking entity.

    Tracks user's progress towards unlocking an achievement.
    """

    user_id: UserId
    achievement_id: AchievementId
    progress_percentage: float
    last_updated: datetime
    missing_requirements: list[str] = field(default_factory=list)
    is_eligible: bool = False

    def __post_init__(self):
        """Validate progress data after initialization"""
        if not (0.0 <= self.progress_percentage <= 100.0):
            raise ValueError("Progress percentage must be between 0 and 100")

    def update_progress(
        self, new_percentage: float, missing_reqs: list[str], eligible: bool
    ) -> None:
        """Update progress information"""
        if not (0.0 <= new_percentage <= 100.0):
            raise ValueError("Progress percentage must be between 0 and 100")

        self.progress_percentage = new_percentage
        self.missing_requirements = missing_reqs
        self.is_eligible = eligible
        self.last_updated = datetime.utcnow()

    def is_close_to_completion(self, threshold: float = 80.0) -> bool:
        """Check if user is close to completing this achievement"""
        return self.progress_percentage >= threshold

    def get_completion_estimate(self) -> str:
        """Get estimated completion status"""
        if self.is_eligible:
            return "Ready to unlock!"
        elif self.progress_percentage >= 90:
            return "Almost there!"
        elif self.progress_percentage >= 75:
            return "Close to completion"
        elif self.progress_percentage >= 50:
            return "Halfway there"
        elif self.progress_percentage >= 25:
            return "Making progress"
        else:
            return "Just getting started"
