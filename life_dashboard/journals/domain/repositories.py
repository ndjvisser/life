"""
Journals domain repositories - abstract interfaces for data access.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from .entities import JournalEntry
from .value_objects import EntryId, UserId


class JournalEntryRepository(ABC):
    """Abstract repository for journal entries."""

    @abstractmethod
    def save(self, entry: JournalEntry) -> JournalEntry:
        """Save a journal entry."""
        pass

    @abstractmethod
    def get_by_id(self, entry_id: EntryId) -> JournalEntry | None:
        """Get a journal entry by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: UserId) -> list[JournalEntry]:
        """Get all journal entries for a user."""
        pass

    @abstractmethod
    def get_by_user_and_date_range(
        self, user_id: UserId, start_date: datetime, end_date: datetime
    ) -> list[JournalEntry]:
        """Get journal entries for a user within a date range."""
        pass

    @abstractmethod
    def delete(self, entry_id: EntryId) -> bool:
        """Delete a journal entry."""
        pass

    @abstractmethod
    def search_by_content(self, user_id: UserId, query: str) -> list[JournalEntry]:
        """Search journal entries by content."""
        pass

    @abstractmethod
    def get_by_tags(self, user_id: UserId, tags: list[str]) -> list[JournalEntry]:
        """Get journal entries by tags."""
        pass
