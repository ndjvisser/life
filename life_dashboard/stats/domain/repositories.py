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
        """Get core stats by user ID."""
        pass

    @abstractmethod
    def save(self, core_stat: CoreStat) -> CoreStat:
        """Save core stats and return updated entity."""
        pass

    @abstractmethod
    def create(self, core_stat: CoreStat) -> CoreStat:
        """Create new core stats."""
        pass

    @abstractmethod
    def exists_by_user_id(self, user_id: int) -> bool:
        """Check if core stats exist for user ID."""
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
        """Get all life stats for a user."""
        pass

    @abstractmethod
    def get_by_category(self, user_id: int, category: str) -> List[LifeStat]:
        """Get life stats by user ID and category."""
        pass

    @abstractmethod
    def save(self, life_stat: LifeStat) -> LifeStat:
        """Save life stat and return updated entity."""
        pass

    @abstractmethod
    def create(self, life_stat: LifeStat) -> LifeStat:
        """Create new life stat."""
        pass

    @abstractmethod
    def delete(self, user_id: int, category: str, name: str) -> bool:
        """Delete life stat."""
        pass

    @abstractmethod
    def get_categories_for_user(self, user_id: int) -> List[str]:
        """Get all categories that have stats for a user."""
        pass


class StatHistoryRepository(ABC):
    """Abstract repository for StatHistory persistence."""

    @abstractmethod
    def create(self, stat_history: StatHistory) -> StatHistory:
        """Create new stat history entry."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[StatHistory]:
        """Get stat history for user, most recent first."""
        pass

    @abstractmethod
    def get_by_stat(
        self, user_id: int, stat_type: str, stat_name: str, limit: int = 50
    ) -> List[StatHistory]:
        """Get history for a specific stat."""
        pass

    @abstractmethod
    def get_by_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> List[StatHistory]:
        """Get stat history within date range."""
        pass

    @abstractmethod
    def get_summary_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for recent period."""
        pass
