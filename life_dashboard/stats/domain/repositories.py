"""
Stats domain repository interfaces - abstract data access contracts.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from .entities import CoreStat, LifeStat, StatHistory


class CoreStatRepository(ABC):
    """Abstract repository for CoreStat persistence."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[CoreStat]:
        """
        Return the CoreStat for the given user ID, or None if no core stats exist.
        
        Returns:
            Optional[CoreStat]: The user's CoreStat instance, or None when not found.
        """
        pass

    @abstractmethod
    def save(self, core_stat: CoreStat) -> CoreStat:
        """Save core stats and return updated entity."""
        pass

    @abstractmethod
    def create(self, core_stat: CoreStat) -> CoreStat:
        """
        Create and persist a new CoreStat entity.
        
        Accepts a CoreStat (typically without persistence metadata) and stores it in the repository,
        returning the persisted CoreStat (may include generated identifiers or timestamps).
        """
        pass

    @abstractmethod
    def exists_by_user_id(self, user_id: int) -> bool:
        """
        Return True if a CoreStat exists for the given user ID, otherwise False.
        
        Parameters:
            user_id (int): ID of the user to check.
        
        Returns:
            bool: True when a CoreStat record exists for `user_id`, False if not.
        """
        pass


class LifeStatRepository(ABC):
    """Abstract repository for LifeStat persistence."""

    @abstractmethod
    def get_by_user_and_name(
        self, user_id: int, category: str, name: str
    ) -> Optional[LifeStat]:
        """Get life stat by user ID, category, and name."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[LifeStat]:
        """
        Return all LifeStat records belonging to the specified user.
        
        Returns a list of LifeStat entities for the given user_id. If the user has no life stats, an empty list is returned.
        """
        pass

    @abstractmethod
    def get_by_category(self, user_id: int, category: str) -> List[LifeStat]:
        """
        Return all LifeStat records for a user filtered by category.
        
        Parameters:
            user_id (int): ID of the user whose stats to retrieve.
            category (str): Category name to filter the user's life stats.
        
        Returns:
            List[LifeStat]: A list of LifeStat objects matching the given user and category; empty if none found.
        """
        pass

    @abstractmethod
    def save(self, life_stat: LifeStat) -> LifeStat:
        """
        Persist the given LifeStat and return the saved entity.
        
        Parameters:
            life_stat (LifeStat): The LifeStat to persist. The returned instance reflects any repository-side changes (for example, updated timestamps or generated identifiers).
        
        Returns:
            LifeStat: The persisted LifeStat.
        """
        pass

    @abstractmethod
    def create(self, life_stat: LifeStat) -> LifeStat:
        """
        Create and persist a new LifeStat.
        
        Parameters:
            life_stat (LifeStat): The LifeStat entity to create.
        
        Returns:
            LifeStat: The created LifeStat as returned by the repository (may include repository-assigned fields).
        """
        pass

    @abstractmethod
    def delete(self, user_id: int, category: str, name: str) -> bool:
        """
        Delete a life stat identified by user, category, and name.
        
        Deletes the life stat record for the given user_id, category, and name. Returns True if a record was removed, False if no matching record existed.
        """
        pass

    @abstractmethod
    def get_categories_for_user(self, user_id: int) -> List[str]:
        """
        Return the list of distinct stat categories that have entries for the given user.
        
        Parameters:
            user_id (int): ID of the user whose stat categories are requested.
        
        Returns:
            List[str]: A list of category names that have at least one stat for the user. Returns an empty list if the user has no categories.
        """
        pass


class StatHistoryRepository(ABC):
    """Abstract repository for StatHistory persistence."""

    @abstractmethod
    def create(self, stat_history: StatHistory) -> StatHistory:
        """
        Create a new StatHistory entry in the persistence layer and return the stored entity.
        
        Persist the provided `stat_history` entity and return the saved instance as stored by the repository.
        The returned object may include repository-generated fields (for example IDs or timestamps) that were
        not present on the input instance.
        
        Parameters:
            stat_history (StatHistory): The history record to persist.
        
        Returns:
            StatHistory: The persisted StatHistory with any repository-assigned fields populated.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[StatHistory]:
        """
        Retrieve a user's stat history ordered most-recent-first.
        
        Parameters:
            user_id (int): ID of the user whose history to fetch.
            limit (int): Maximum number of entries to return (default: 100).
        
        Returns:
            List[StatHistory]: A list of StatHistory entries ordered from newest to oldest; may be empty.
        """
        pass

    @abstractmethod
    def get_by_stat(
        self, user_id: int, stat_type: str, stat_name: str, limit: int = 50
    ) -> List[StatHistory]:
        """
        Return the recent history entries for a specific stat (most recent first).
        
        Detailed description:
        Retrieves up to `limit` StatHistory records for the stat identified by `stat_type` and `stat_name` belonging to `user_id`. Results are ordered with the most recent entries first.
        
        Parameters:
            user_id (int): ID of the user who owns the stat.
            stat_type (str): Category or type of the stat (e.g., "core", "life").
            stat_name (str): Name/identifier of the stat within its type.
            limit (int): Maximum number of history entries to return (default: 50).
        
        Returns:
            List[StatHistory]: A list of StatHistory entries, newest first.
        """
        pass

    @abstractmethod
    def get_by_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> List[StatHistory]:
        """
        Return stat history entries for a user that fall within a given date range.
        
        Parameters:
            user_id (int): ID of the user whose history to retrieve.
            start_date (date): Lower bound of the date range.
            end_date (date): Upper bound of the date range.
        
        Returns:
            List[StatHistory]: StatHistory records for the user with recorded dates between start_date and end_date.
        """
        pass

    @abstractmethod
    def get_summary_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Return summary statistics for a user's recent stat history.
        
        Retrieves aggregated statistics covering the most recent `days` days for the given user.
        `days` is the number of days up to and including today to include in the summary (default 30).
        
        Parameters:
            user_id (int): ID of the user whose stats are summarized.
            days (int): Time window in days to include in the summary; defaults to 30.
        
        Returns:
            Dict[str, Any]: A dictionary of summary metrics where keys are metric names and values
            are the corresponding aggregated results (e.g., counts, averages, totals, or other
            computed summaries).
        """
        pass
