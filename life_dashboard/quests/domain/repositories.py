"""
Quests domain repository interfaces - abstract data access contracts.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from .entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestStatus,
    QuestType,
)


class QuestRepository(ABC):
    """Abstract repository for Quest persistence."""

    @abstractmethod
    def get_by_id(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Quest]:
        """Get all quests for a user."""
        pass

    @abstractmethod
    def get_by_status(self, user_id: int, status: QuestStatus) -> List[Quest]:
        """Get quests by status for a user."""
        pass

    @abstractmethod
    def get_by_type(self, user_id: int, quest_type: QuestType) -> List[Quest]:
        """Get quests by type for a user."""
        pass

    @abstractmethod
    def save(self, quest: Quest) -> Quest:
        """Save quest and return updated entity."""
        pass

    @abstractmethod
    def create(self, quest: Quest) -> Quest:
        """Create new quest."""
        pass

    @abstractmethod
    def delete(self, quest_id: str) -> bool:
        """Delete quest."""
        pass

    @abstractmethod
    def get_overdue_quests(self, user_id: int) -> List[Quest]:
        """Get overdue quests for a user."""
        pass

    @abstractmethod
    def get_due_soon(self, user_id: int, days: int = 7) -> List[Quest]:
        """Get quests due within specified days."""
        pass

    @abstractmethod
    def get_by_parent_quest(self, parent_quest_id: str) -> List[Quest]:
        """Get child quests of a parent quest."""
        pass

    @abstractmethod
    def search_quests(self, user_id: int, query: str, limit: int = 20) -> List[Quest]:
        """Search quests by title or description."""
        pass


class HabitRepository(ABC):
    """Abstract repository for Habit persistence."""

    @abstractmethod
    def get_by_id(self, habit_id: str) -> Optional[Habit]:
        """Get habit by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Habit]:
        """Get all habits for a user."""
        pass

    @abstractmethod
    def get_by_frequency(self, user_id: int, frequency: HabitFrequency) -> List[Habit]:
        """Get habits by frequency for a user."""
        pass

    @abstractmethod
    def save(self, habit: Habit) -> Habit:
        """Save habit and return updated entity."""
        pass

    @abstractmethod
    def create(self, habit: Habit) -> Habit:
        """Create new habit."""
        pass

    @abstractmethod
    def delete(self, habit_id: str) -> bool:
        """Delete habit."""
        pass

    @abstractmethod
    def get_due_today(self, user_id: int) -> List[Habit]:
        """Get habits due today for a user."""
        pass

    @abstractmethod
    def get_active_streaks(self, user_id: int, min_streak: int = 7) -> List[Habit]:
        """Get habits with active streaks above minimum."""
        pass

    @abstractmethod
    def search_habits(self, user_id: int, query: str, limit: int = 20) -> List[Habit]:
        """Search habits by name or description."""
        pass


class HabitCompletionRepository(ABC):
    """Abstract repository for HabitCompletion persistence."""

    @abstractmethod
    def create(self, completion: HabitCompletion) -> HabitCompletion:
        """Create new habit completion."""
        pass

    @abstractmethod
    def get_by_habit_id(self, habit_id: str, limit: int = 100) -> List[HabitCompletion]:
        """Get completions for a habit."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[HabitCompletion]:
        """Get completions for a user."""
        pass

    @abstractmethod
    def get_by_date_range(
        self, habit_id: str, start_date: date, end_date: date
    ) -> List[HabitCompletion]:
        """Get completions within date range."""
        pass

    @abstractmethod
    def get_completion_for_date(
        self, habit_id: str, completion_date: date
    ) -> Optional[HabitCompletion]:
        """Get completion for specific date."""
        pass

    @abstractmethod
    def delete_completion(self, completion_id: str) -> bool:
        """Delete habit completion."""
        pass

    @abstractmethod
    def get_streak_data(self, habit_id: str, days: int = 365) -> List[HabitCompletion]:
        """Get completion data for streak calculation."""
        pass

    @abstractmethod
    def get_completion_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get completion statistics for user."""
        pass
