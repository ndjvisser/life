"""
Quest Domain Repositories

Abstract repository interfaces for quest data access.
No Django dependencies allowed in this module.
"""

from abc import ABC, abstractmethod
from datetime import date

from .entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestStatus,
    QuestType,
)
from .value_objects import HabitId, QuestId, UserId


class QuestRepository(ABC):
    """Abstract repository for quest data access"""

    @abstractmethod
    def create(self, quest: Quest) -> Quest:
        """Create a quest entity"""
        raise NotImplementedError

    @abstractmethod
    def save(self, quest: Quest) -> Quest:
        """Save a quest entity"""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, quest_id: QuestId | str) -> Quest | None:
        """Get quest by ID"""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UserId | int) -> list[Quest]:
        """Get quests for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_user_quests(self, user_id: UserId | int) -> list[Quest]:
        """Get all quests for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_by_status(self, user_id: UserId | int, status: QuestStatus) -> list[Quest]:
        """Get quests filtered by status for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_by_type(self, user_id: UserId | int, quest_type: QuestType) -> list[Quest]:
        """Get quests filtered by type for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_active_quests(self, user_id: UserId | int) -> list[Quest]:
        """Get active quests for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_overdue_quests(self, user_id: UserId | int) -> list[Quest]:
        """Get overdue quests for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_due_soon(self, user_id: UserId | int, days: int = 7) -> list[Quest]:
        """Get quests due within a window"""
        raise NotImplementedError

    @abstractmethod
    def search_quests(
        self, user_id: UserId | int, query: str, limit: int = 20
    ) -> list[Quest]:
        """Search quests for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_by_parent_quest(self, parent_quest_id: QuestId | str) -> list[Quest]:
        """Get child quests for a parent quest"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, quest_id: QuestId) -> bool:
        """Delete a quest"""
        raise NotImplementedError


class HabitRepository(ABC):
    """Abstract repository for habit data access"""

    @abstractmethod
    def create(self, habit: Habit) -> Habit:
        """Create a habit entity"""
        raise NotImplementedError

    @abstractmethod
    def save(self, habit: Habit) -> Habit:
        """Save a habit entity"""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, habit_id: HabitId) -> Habit | None:
        """Get habit by ID"""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UserId) -> list[Habit]:
        """Get habits for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_user_habits(self, user_id: UserId) -> list[Habit]:
        """Get all habits for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_by_frequency(
        self, user_id: UserId, frequency: HabitFrequency
    ) -> list[Habit]:
        """Get habits filtered by frequency for a user"""
        raise NotImplementedError

    @abstractmethod
    def get_due_today(self, user_id: UserId) -> list[Habit]:
        """Get habits due today"""
        raise NotImplementedError

    @abstractmethod
    def get_active_streaks(self, user_id: UserId, min_streak: int = 7) -> list[Habit]:
        """Get habits with streaks above a minimum"""
        raise NotImplementedError

    @abstractmethod
    def search_habits(
        self, user_id: UserId, query: str, limit: int = 20
    ) -> list[Habit]:
        """Search habits for a user"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, habit_id: HabitId) -> bool:
        """Delete a habit"""
        raise NotImplementedError


class HabitCompletionRepository(ABC):
    """Abstract repository for habit completion data access"""

    @abstractmethod
    def create(self, completion: HabitCompletion) -> HabitCompletion:
        """Create a habit completion entity"""
        raise NotImplementedError

    @abstractmethod
    def save(self, completion: HabitCompletion) -> HabitCompletion:
        """Save a habit completion"""
        raise NotImplementedError

    @abstractmethod
    def get_habit_completions(
        self,
        habit_id: HabitId,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[HabitCompletion]:
        """Get completions for a habit within date range"""
        raise NotImplementedError

    @abstractmethod
    def get_latest_completion(self, habit_id: HabitId) -> HabitCompletion | None:
        """Get the most recent completion for a habit"""
        raise NotImplementedError

    @abstractmethod
    def get_completion_count(self, habit_id: HabitId, target_date: date) -> int:
        """Get completion count for a specific date"""
        raise NotImplementedError

    @abstractmethod
    def get_completion_for_date(
        self, habit_id: HabitId, target_date: date
    ) -> HabitCompletion | None:
        """Get a completion for a specific date"""
        raise NotImplementedError

    @abstractmethod
    def get_by_habit_id(
        self, habit_id: HabitId, limit: int | None = None
    ) -> list[HabitCompletion]:
        """Get completions for a habit"""
        raise NotImplementedError

    @abstractmethod
    def delete_completion(self, completion_id: str) -> bool:
        """Delete a habit completion by its identifier"""
        raise NotImplementedError

    @abstractmethod
    def get_by_date_range(
        self, habit_id: HabitId, start_date: date, end_date: date
    ) -> list[HabitCompletion]:
        """Get completions within a date range"""
        raise NotImplementedError

    @abstractmethod
    def get_completion_stats(
        self, user_id: UserId, days: int = 30
    ) -> dict[str, int | float]:
        """Get aggregated completion statistics for a user"""
        raise NotImplementedError
