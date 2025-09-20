"""
Journals domain entities - pure Python business logic without Django dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EntryType(Enum):
    """Journal entry types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MILESTONE = "milestone"
    INSIGHT = "insight"


@dataclass
class JournalEntry:
    """Pure domain entity for journal entries."""

    entry_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    title: str = ""
    content: str = ""
    entry_type: EntryType = EntryType.DAILY

    # Related items
    related_quest_id: Optional[str] = None
    related_achievement_id: Optional[str] = None

    # Mood and tags
    mood: Optional[int] = None
    tags: List[str] = field(default_factory=list)

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Perform post-initialization validation for a JournalEntry.

        Ensures the required `title` is present and, if `mood` is set, that it falls between 1 and 10 inclusive.
        Raises ValueError when either validation fails.
        """
        if not self.title:
            raise ValueError("Journal entry title is required")

        if self.mood is not None and not 1 <= self.mood <= 10:
            raise ValueError("Mood rating must be between 1 and 10")

    def update_content(self, title: str, content: str) -> None:
        """
        Update the entry's title and content and refresh its updated_at timestamp.

        Parameters:
            title (str): New title for the entry.
            content (str): New content/body for the entry.

        Side effects:
            Sets `self.updated_at` to the current UTC time.
        """
        self.title = title
        self.content = content
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """
        Add a non-empty, unique tag to the entry.

        If `tag` is empty or already present, the tags list is unchanged. When a tag is added, `updated_at` is set to the current UTC time.
        """
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the entry.

        If the tag is present in the entry's tags list it is removed and updated_at is set to the current UTC time.
        If the tag is not present, the method is a no-op.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def set_mood(self, mood: int) -> None:
        """
        Set the entry's mood rating and refresh the updated_at timestamp.

        Parameters:
            mood (int): Mood rating from 1 (lowest) to 10 (highest).

        Raises:
            ValueError: If `mood` is not between 1 and 10 (inclusive).
        """
        if not 1 <= mood <= 10:
            raise ValueError("Mood rating must be between 1 and 10")

        self.mood = mood
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the JournalEntry suitable for serialization.

        The returned mapping includes all primary fields. `entry_type` is returned as its string value.
        `created_at` and `updated_at` are ISO 8601 strings when present, otherwise None. Lists and
        primitive fields are returned as-is (e.g., `tags` is a list of strings).
        Returns:
            Dict[str, Any]: Dictionary containing the entry's data keyed by field name.
        """
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "entry_type": self.entry_type.value,
            "related_quest_id": self.related_quest_id,
            "related_achievement_id": self.related_achievement_id,
            "mood": self.mood,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
