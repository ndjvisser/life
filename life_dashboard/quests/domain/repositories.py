"""
Quest Domain Repositories

Abstract repository interfaces for quest data access.
No Django dependencies allowed in this module.
"""

from abc import ABC, abstractmethod
from datetime import date

from .entities import Habit, HabitCompletion, Quest
from .value_objects import HabitId, QuestId, UserId


class QuestRepository(ABC):
    """Abstract repository for quest data access"""

    @abstractmethod
    def save(self, quest: Quest) -> Quest:
        """Save a quest entity"""
        pass

    @abstractmethod
    def get_by_id(self, quest_id: QuestId) -> Quest | None:
        """Get quest by ID"""
        pass

    @abstractmethod
    def get_user_quests(self, user_id: UserId) -> list[Quest]:
        """Get all quests for a user"""
        pass

    @abstractmethod
    def get_active_quests(self, user_id: UserId) -> list[Quest]:
        """Get active quests for a user"""
        pass

    @abstractmethod
    def get_overdue_quests(self, user_id: UserId) -> list[Quest]:
        """Get overdue quests for a user"""
        pass

    @abstractmethod
    def delete(self, quest_id: QuestId) -> bool:
        """Delete a quest"""
        pass


class HabitRepository(ABC):
    """Abstract repository for habit data access"""

    @abstractmethod
    def save(self, habit: Habit) -> Habit:
        """Save a habit entity"""
        pass

    @abstractmethod
    def get_by_id(self, habit_id: HabitId) -> Habit | None:
        """Get habit by ID"""
        pass

    @abstractmethod
    def get_user_habits(self, user_id: UserId) -> list[Habit]:
        """Get all habits for a user"""
        pass

    @abstractmethod
    def delete(self, habit_id: HabitId) -> bool:
        """Delete a habit"""
        pass


class HabitCompletionRepository(ABC):
    """Abstract repository for habit completion data access"""

    @abstractmethod
    def save(self, completion: HabitCompletion) -> HabitCompletion:
        """Save a habit completion"""
        pass

    @abstractmethod
    def get_habit_completions(
        self,
        habit_id: HabitId,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[HabitCompletion]:
        """Get completions for a habit within date range"""
        pass

    @abstractmethod
    def get_latest_completion(self, habit_id: HabitId) -> HabitCompletion | None:
        """Get the most recent completion for a habit"""
        pass

    @abstractmethod
    def get_completion_count(self, habit_id: HabitId, target_date: date) -> int:
        """Get completion count for a specific date"""
        pass
