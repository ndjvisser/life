"""
Journals domain services - business logic orchestration.
"""

from datetime import datetime, timedelta

from .entities import EntryType, JournalEntry
from .repositories import JournalEntryRepository
from .value_objects import EntryContent, EntryId, EntryTitle, MoodRating, Tag, UserId


class JournalService:
    """Service for journal entry business logic."""

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def create_entry(
        self,
        user_id: int,
        title: str,
        content: str,
        entry_type: EntryType = EntryType.DAILY,
        mood: int | None = None,
        tags: list[str] | None = None,
        related_quest_id: str | None = None,
        related_achievement_id: str | None = None,
    ) -> JournalEntry:
        """Create a new journal entry with validation."""
        # Validate inputs using value objects
        user_id_vo = UserId(user_id)
        title_vo = EntryTitle(title)
        content_vo = EntryContent(content)

        mood_vo = None
        if mood is not None:
            mood_vo = MoodRating(mood)

        # Validate and normalize tags
        validated_tags = []
        if tags:
            for tag_str in tags:
                tag_vo = Tag(tag_str)
                validated_tags.append(tag_vo.normalized())

        # Create entry
        entry = JournalEntry(
            user_id=user_id_vo.value,
            title=title_vo.value,
            content=content_vo.value,
            entry_type=entry_type,
            mood=mood_vo.value if mood_vo else None,
            tags=validated_tags,
            related_quest_id=related_quest_id,
            related_achievement_id=related_achievement_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return self.repository.save(entry)

    def update_entry(
        self,
        entry_id: str,
        title: str | None = None,
        content: str | None = None,
        mood: int | None = None,
        tags: list[str] | None = None,
    ) -> JournalEntry | None:
        """Update an existing journal entry."""
        entry_id_vo = EntryId(entry_id)
        entry = self.repository.get_by_id(entry_id_vo)

        if not entry:
            return None

        # Update fields if provided
        if title is not None:
            title_vo = EntryTitle(title)
            entry.title = title_vo.value

        if content is not None:
            content_vo = EntryContent(content)
            entry.content = content_vo.value

        if mood is not None:
            mood_vo = MoodRating(mood)
            entry.mood = mood_vo.value

        if tags is not None:
            validated_tags = []
            for tag_str in tags:
                tag_vo = Tag(tag_str)
                validated_tags.append(tag_vo.normalized())
            entry.tags = validated_tags

        entry.updated_at = datetime.utcnow()
        return self.repository.save(entry)

    def get_user_entries(self, user_id: int) -> list[JournalEntry]:
        """Get all journal entries for a user."""
        user_id_vo = UserId(user_id)
        return self.repository.get_by_user(user_id_vo)

    def get_entries_by_date_range(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> list[JournalEntry]:
        """Get journal entries within a date range."""
        user_id_vo = UserId(user_id)
        return self.repository.get_by_user_and_date_range(
            user_id_vo, start_date, end_date
        )

    def search_entries(self, user_id: int, query: str) -> list[JournalEntry]:
        """Search journal entries by content."""
        user_id_vo = UserId(user_id)
        return self.repository.search_by_content(user_id_vo, query)

    def get_entries_by_tags(self, user_id: int, tags: list[str]) -> list[JournalEntry]:
        """Get journal entries by tags."""
        user_id_vo = UserId(user_id)
        # Normalize tags for search
        normalized_tags = []
        for tag_str in tags:
            tag_vo = Tag(tag_str)
            normalized_tags.append(tag_vo.normalized())

        return self.repository.get_by_tags(user_id_vo, normalized_tags)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        entry_id_vo = EntryId(entry_id)
        return self.repository.delete(entry_id_vo)

    def get_mood_statistics(self, user_id: int, days: int = 30) -> dict:
        """Get mood statistics for a user over the last N days."""
        user_id_vo = UserId(user_id)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        entries = self.repository.get_by_user_and_date_range(
            user_id_vo, start_date, end_date
        )

        moods = [entry.mood for entry in entries if entry.mood is not None]

        if not moods:
            return {
                "average_mood": None,
                "mood_count": 0,
                "positive_days": 0,
                "negative_days": 0,
                "neutral_days": 0,
            }

        positive_count = sum(1 for mood in moods if mood >= 6)
        negative_count = sum(1 for mood in moods if mood <= 4)
        neutral_count = sum(1 for mood in moods if mood == 5)

        return {
            "average_mood": sum(moods) / len(moods),
            "mood_count": len(moods),
            "positive_days": positive_count,
            "negative_days": negative_count,
            "neutral_days": neutral_count,
        }
