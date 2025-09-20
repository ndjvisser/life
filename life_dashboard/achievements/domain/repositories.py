"""
Achievements Domain Repositories

Abstract repository interfaces for achievements data access.
No Django dependencies allowed in this module.
"""

from abc import ABC, abstractmethod

from .entities import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
from .value_objects import AchievementId, UserAchievementId, UserId


class AchievementRepository(ABC):
    """Abstract repository for achievement data access"""

    @abstractmethod
    def save(self, achievement: Achievement) -> Achievement:
        """Save an achievement entity"""
        pass

    @abstractmethod
    def get_by_id(self, achievement_id: AchievementId) -> Achievement | None:
        """Get achievement by ID"""
        pass

    @abstractmethod
    def get_all_achievements(self) -> list[Achievement]:
        """Get all achievements"""
        pass

    @abstractmethod
    def get_achievements_by_tier(self, tier: AchievementTier) -> list[Achievement]:
        """Get achievements by tier"""
        pass

    @abstractmethod
    def get_achievements_by_category(
        self, category: AchievementCategory
    ) -> list[Achievement]:
        """Get achievements by category"""
        pass

    @abstractmethod
    def get_visible_achievements(self) -> list[Achievement]:
        """Get all non-hidden achievements"""
        pass

    @abstractmethod
    def delete(self, achievement_id: AchievementId) -> bool:
        """Delete an achievement"""
        pass


class UserAchievementRepository(ABC):
    """Abstract repository for user achievement data access"""

    @abstractmethod
    def save(self, user_achievement: UserAchievement) -> UserAchievement:
        """Save a user achievement entity"""
        pass

    @abstractmethod
    def get_by_id(
        self, user_achievement_id: UserAchievementId
    ) -> UserAchievement | None:
        """Get user achievement by ID"""
        pass

    @abstractmethod
    def get_user_achievements(self, user_id: UserId) -> list[UserAchievement]:
        """Get all achievements for a user"""
        pass

    @abstractmethod
    def get_user_achievements_by_tier(
        self, user_id: UserId, tier: AchievementTier
    ) -> list[UserAchievement]:
        """Get user achievements by tier"""
        pass

    @abstractmethod
    def get_recent_achievements(
        self, user_id: UserId, days: int = 7
    ) -> list[UserAchievement]:
        """Get recently unlocked achievements for a user"""
        pass

    @abstractmethod
    def has_achievement(self, user_id: UserId, achievement_id: AchievementId) -> bool:
        """Check if user has unlocked a specific achievement"""
        pass

    @abstractmethod
    def get_achievement_count(self, user_id: UserId) -> int:
        """Get total number of achievements unlocked by user"""
        pass

    @abstractmethod
    def delete(self, user_achievement_id: UserAchievementId) -> bool:
        """Delete a user achievement"""
        pass


class AchievementProgressRepository(ABC):
    """Abstract repository for achievement progress data access"""

    @abstractmethod
    def save(self, progress: AchievementProgress) -> AchievementProgress:
        """Save achievement progress"""
        pass

    @abstractmethod
    def get_user_progress(self, user_id: UserId) -> list[AchievementProgress]:
        """Get all achievement progress for a user"""
        pass

    @abstractmethod
    def get_progress_for_achievement(
        self, user_id: UserId, achievement_id: AchievementId
    ) -> AchievementProgress | None:
        """Get progress for a specific achievement"""
        pass

    @abstractmethod
    def get_eligible_achievements(self, user_id: UserId) -> list[AchievementProgress]:
        """Get achievements user is eligible to unlock"""
        pass

    @abstractmethod
    def get_close_to_completion(
        self, user_id: UserId, threshold: float = 80.0
    ) -> list[AchievementProgress]:
        """Get achievements close to completion"""
        pass

    @abstractmethod
    def delete_user_progress(self, user_id: UserId) -> bool:
        """Delete all progress for a user"""
        pass
