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
        """
        Retrieve a Quest by its unique identifier.
        
        Parameters:
            quest_id (str): Unique identifier of the quest.
        
        Returns:
            Optional[Quest]: The Quest if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Quest]:
        """
        Return all Quest entities belonging to the given user.
        
        Parameters:
            user_id (int): ID of the user whose quests to retrieve.
        
        Returns:
            List[Quest]: A list of Quest objects for the user; empty if none exist.
        """
        pass

    @abstractmethod
    def get_by_status(self, user_id: int, status: QuestStatus) -> List[Quest]:
        """
        Retrieve all quests for a user filtered by the given status.
        
        Parameters:
            user_id (int): ID of the user whose quests are being queried.
            status (QuestStatus): Status to filter quests by (e.g., active, completed).
        
        Returns:
            List[Quest]: A list of Quest entities matching the user and status. Returns an empty list if none are found.
        """
        pass

    @abstractmethod
    def get_by_type(self, user_id: int, quest_type: QuestType) -> List[Quest]:
        """
        Return all quests of a specific type for a given user.
        
        Retrieves quests belonging to the user identified by `user_id` that match the provided `quest_type` filter.
        
        Parameters:
            user_id (int): ID of the user whose quests to search.
            quest_type (QuestType): Quest type to filter by.
        
        Returns:
            List[Quest]: A list of quests for the user that have the specified type. Empty list if none found.
        """
        pass

    @abstractmethod
    def save(self, quest: Quest) -> Quest:
        """
        Save updates to an existing Quest and return the persisted entity.
        
        The provided `Quest` should represent an existing record (identifier set). Implementations must persist modifications from `quest` and return the stored instance, including any persistence-populated fields (for example updated timestamps or version data).
        
        Returns:
            Quest: The persisted Quest with persistence-layer modifications applied.
        """
        pass

    @abstractmethod
    def create(self, quest: Quest) -> Quest:
        """
        Create and persist a new Quest entity.
        
        Parameters:
            quest (Quest): Quest to create; implementation may populate/override persistence-generated fields (e.g., id, timestamps).
        
        Returns:
            Quest: The newly created Quest with persistence-populated fields.
        """
        pass

    @abstractmethod
    def delete(self, quest_id: str) -> bool:
        """
        Delete a quest by its ID.
        
        Parameters:
            quest_id (str): Unique identifier of the quest to delete.
        
        Returns:
            bool: True if the quest was successfully deleted, False if no quest was found with the given ID or deletion failed.
        """
        pass

    @abstractmethod
    def get_overdue_quests(self, user_id: int) -> List[Quest]:
        """
        Return quests for a user that are currently overdue.
        
        Detailed behavior depends on the repository implementation, but implementations should return quests belonging to the given user that are considered overdue (for example, past their due date and not completed).
        
        Parameters:
            user_id (int): ID of the user whose overdue quests should be retrieved.
        
        Returns:
            List[Quest]: A list of overdue Quest entities for the user (empty if none).
        """
        pass

    @abstractmethod
    def get_due_soon(self, user_id: int, days: int = 7) -> List[Quest]:
        """
        Return quests for a user that are due within the next `days` days.
        
        Retrieves quests owned by the specified user whose due date falls within the upcoming lookahead window.
        Parameters:
            user_id (int): ID of the user whose quests to search.
            days (int, optional): Number of days from today to consider as the "due soon" window. Defaults to 7.
        
        Returns:
            List[Quest]: List of quests with due dates within the next `days` days (may be empty).
        """
        pass

    @abstractmethod
    def get_by_parent_quest(self, parent_quest_id: str) -> List[Quest]:
        """
        Return all child Quest entities whose parent is the given quest ID.
        
        Parameters:
            parent_quest_id (str): ID of the parent quest.
        
        Returns:
            List[Quest]: Child quests for the parent quest; empty list if none are found.
        """
        pass

    @abstractmethod
    def search_quests(self, user_id: int, query: str, limit: int = 20) -> List[Quest]:
        """
        Search quests for a specific user by matching the query against quest title or description.
        
        Search is scoped to the provided user_id and returns at most `limit` results (default 20). The `query` is used as a textual match against quest title and description; implementations may use case-insensitive or partial matching.
        Parameters:
            user_id (int): ID of the user whose quests should be searched.
            query (str): Text to match against quest title or description.
            limit (int): Maximum number of quests to return (default 20).
        
        Returns:
            List[Quest]: A list of quests matching the query, up to `limit` items.
        """
        pass


class HabitRepository(ABC):
    """Abstract repository for Habit persistence."""

    @abstractmethod
    def get_by_id(self, habit_id: str) -> Optional[Habit]:
        """
        Retrieve a Habit by its identifier.
        
        Parameters:
            habit_id (str): The unique identifier of the habit to retrieve.
        
        Returns:
            Optional[Habit]: The Habit if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Habit]:
        """
        Return all Habit entities belonging to the specified user.
        
        Parameters:
            user_id (int): ID of the user whose habits should be retrieved.
        
        Returns:
            List[Habit]: A list of the user's habits. Returns an empty list if the user has no habits.
        """
        pass

    @abstractmethod
    def get_by_frequency(self, user_id: int, frequency: HabitFrequency) -> List[Habit]:
        """
        Return habits for a user filtered by frequency.
        
        Parameters:
            user_id (int): ID of the user who owns the habits.
            frequency (HabitFrequency): Frequency value used to filter the user's habits.
        
        Returns:
            List[Habit]: Habits belonging to the user that match the specified frequency. Returns an empty list if none are found.
        """
        pass

    @abstractmethod
    def save(self, habit: Habit) -> Habit:
        """
        Persist updates to an existing Habit and return the updated entity.
        
        Parameters:
            habit (Habit): Habit entity with changes to persist. The implementation may refresh fields (e.g. timestamps, derived fields, or version) before returning.
        
        Returns:
            Habit: The persisted Habit instance reflecting any modifications applied by the storage layer.
        """
        pass

    @abstractmethod
    def create(self, habit: Habit) -> Habit:
        """
        Create a new Habit record in the repository and return the persisted entity.
        
        The returned Habit should include any repository-assigned fields (for example an ID or timestamps) populated by the persistence layer.
        
        Parameters:
            habit (Habit): Habit entity to create; may omit persistence-assigned fields (e.g., `id`) which will be filled on creation.
        
        Returns:
            Habit: The created Habit with persistence-assigned fields populated.
        """
        pass

    @abstractmethod
    def delete(self, habit_id: str) -> bool:
        """
        Delete a habit by its ID.
        
        Parameters:
            habit_id (str): The unique identifier of the habit to remove.
        
        Returns:
            bool: True if the habit was successfully deleted, False if no habit with the given ID existed or deletion failed.
        """
        pass

    @abstractmethod
    def get_due_today(self, user_id: int) -> List[Habit]:
        """
        Return habits that are due today for the specified user.
        
        Determines which of the user's habits are scheduled or flagged as due on the current date and returns them as a list. Implementations should consider the user's timezone and habit scheduling rules (recurrence, next due date). Returns an empty list if no habits are due.
        """
        pass

    @abstractmethod
    def get_active_streaks(self, user_id: int, min_streak: int = 7) -> List[Habit]:
        """
        Return the user's habits that currently have an active completion streak at or above `min_streak`.
        
        Searches habits owned by `user_id` and returns those whose current consecutive-day completion streak meets or exceeds `min_streak` (default 7). The returned list contains Habit entities ordered by descending streak length when available.
        
        Args:
            user_id (int): ID of the user whose habits to evaluate.
            min_streak (int): Minimum current consecutive-day streak required to include a habit.
        
        Returns:
            List[Habit]: Habits for the user with active streaks >= `min_streak`.
        """
        pass

    @abstractmethod
    def search_habits(self, user_id: int, query: str, limit: int = 20) -> List[Habit]:
        """
        Search habits for a user by matching the provided query against habit name or description.
        
        The function returns up to `limit` Habit objects that match the `query` for the given `user_id`. The result list may be empty if no habits match.
        
        Parameters:
            query (str): Text to match against habit name or description.
            limit (int): Maximum number of results to return (default 20).
        
        Returns:
            List[Habit]: A list of matching Habit entities (possibly empty).
        """
        pass


class HabitCompletionRepository(ABC):
    """Abstract repository for HabitCompletion persistence."""

    @abstractmethod
    def create(self, completion: HabitCompletion) -> HabitCompletion:
        """
        Create a new HabitCompletion record in the repository.
        
        Parameters:
            completion (HabitCompletion): HabitCompletion entity to persist. May be incomplete (e.g., missing id or created_at); repository implementations are expected to populate any persistence-generated fields.
        
        Returns:
            HabitCompletion: The persisted HabitCompletion, typically including any assigned identifiers or timestamps.
        """
        pass

    @abstractmethod
    def get_by_habit_id(self, habit_id: str, limit: int = 100) -> List[HabitCompletion]:
        """
        Return up to `limit` HabitCompletion records for the given habit ID.
        
        Parameters:
            habit_id (str): Identifier of the habit whose completions to retrieve.
            limit (int): Maximum number of completions to return (default 100).
        
        Returns:
            List[HabitCompletion]: A list of HabitCompletion objects; empty if none are found.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[HabitCompletion]:
        """
        Retrieve habit completion records for a specific user.
        
        Parameters:
            user_id (int): ID of the user whose completions are requested.
            limit (int): Maximum number of completion records to return (default 100).
        
        Returns:
            List[HabitCompletion]: A list containing at most `limit` HabitCompletion records for the user.
        """
        pass

    @abstractmethod
    def get_by_date_range(
        self, habit_id: str, start_date: date, end_date: date
    ) -> List[HabitCompletion]:
        """
        Return habit completions for a habit within a date range (inclusive).
        
        Parameters:
            habit_id (str): ID of the habit to query.
            start_date (date): Start of the range (inclusive).
            end_date (date): End of the range (inclusive).
        
        Returns:
            List[HabitCompletion]: Completions for the habit whose completion dates fall between start_date and end_date, ordered by date (ascending). Returns an empty list if none are found.
        """
        pass

    @abstractmethod
    def get_completion_for_date(
        self, habit_id: str, completion_date: date
    ) -> Optional[HabitCompletion]:
        """
        Return the HabitCompletion for a given habit on a specific date, or None if no completion exists.
        
        Parameters:
            habit_id (str): ID of the habit to query.
            completion_date (date): The date to look up the completion for.
        
        Returns:
            Optional[HabitCompletion]: The completion record for that date, or None when not found.
        """
        pass

    @abstractmethod
    def delete_completion(self, completion_id: str) -> bool:
        """
        Delete a habit completion record by its identifier.
        
        Parameters:
            completion_id (str): Unique identifier of the HabitCompletion to delete.
        
        Returns:
            bool: True if a record was found and deleted; False if no matching record existed.
        """
        pass

    @abstractmethod
    def get_streak_data(self, habit_id: str, days: int = 365) -> List[HabitCompletion]:
        """
        Return habit completions for streak calculations.
        
        Retrieve completion records for the specified habit over the previous `days` days (including today). `days` defaults to 365. Implementations should return HabitCompletion instances covering the requested window; callers use this data to compute current and historical streaks.
        """
        pass

    @abstractmethod
    def get_completion_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Return completion statistics for a user's habit completions over a recent period.
        
        Parameters:
            user_id (int): ID of the user to compute statistics for.
            days (int): Number of past days (including today) to include in the calculation (default 30).
        
        Returns:
            Dict[str, Any]: A dictionary of aggregate statistics. Typical keys:
                - total_completions (int): Total number of completions in the interval.
                - daily_average (float): Average completions per day over the interval.
                - completion_rate (float): Fraction (0.0–1.0) of days with at least one completion.
                - current_streak (int): Number of consecutive days up to today with completions.
                - longest_streak (int): Longest observed consecutive completion streak within the interval.
                - completions_by_day (Dict[str, int]): Mapping of ISO-8601 date strings to completion counts for each day in the interval.
        
        Notes:
            - The function summarizes recorded HabitCompletion entries; absent days are treated as zero completions.
        """
        pass
