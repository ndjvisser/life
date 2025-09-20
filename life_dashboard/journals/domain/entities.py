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
        """Validate journal entry on creation."""
        if not self.title:
            raise ValueError("Journal entry title is required")

        if self.mood is not None and not 1 <= self.mood <= 10:
            raise ValueError("Mood rating must be between 1 and 10")

    def update_content(self, title: str, content: str) -> None:
        """Update entry content."""
        self.title = title
        self.content = content
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entry."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def set_mood(self, mood: int) -> None:
        """Set mood rating."""
        if not 1 <= mood <= 10:
            raise ValueError("Mood rating must be between 1 and 10")

        self.mood = mood
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
