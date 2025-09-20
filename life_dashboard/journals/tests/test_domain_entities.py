"""
Domain entity tests for journals - pure Python business logic tests.
"""

from datetime import datetime, timedelta

import pytest

from life_dashboard.journals.domain.entities import EntryType, JournalEntry


@pytest.mark.domain
@pytest.mark.unit
class TestJournalEntry:
    """Test JournalEntry domain entity."""

    def test_journal_entry_creation_with_valid_data(self):
        """Test creating a journal entry with valid data."""
        entry = JournalEntry(
            user_id=1,
            title="My Daily Reflection",
            content="Today was a good day. I accomplished my goals.",
            entry_type=EntryType.DAILY,
            mood=8,
            tags=["productivity", "goals"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert entry.user_id == 1
        assert entry.title == "My Daily Reflection"
        assert entry.content == "Today was a good day. I accomplished my goals."
        assert entry.entry_type == EntryType.DAILY
        assert entry.mood == 8
        assert entry.tags == ["productivity", "goals"]
        assert entry.entry_id is not None
        assert entry.created_at is not None
        assert entry.updated_at is not None

    def test_journal_entry_requires_title(self):
        """Test that journal entry requires a title."""
        with pytest.raises(ValueError, match="Journal entry title is required"):
            JournalEntry(user_id=1, title="", content="Some content")

    def test_journal_entry_mood_validation(self):
        """Test mood rating validation."""
        # Valid mood
        entry = JournalEntry(user_id=1, title="Test Entry", content="Content", mood=5)
        assert entry.mood == 5

        # Invalid mood - too low
        with pytest.raises(ValueError, match="Mood rating must be between 1 and 10"):
            JournalEntry(user_id=1, title="Test Entry", content="Content", mood=0)

        # Invalid mood - too high
        with pytest.raises(ValueError, match="Mood rating must be between 1 and 10"):
            JournalEntry(user_id=1, title="Test Entry", content="Content", mood=11)

    def test_journal_entry_update_content(self):
        """Test updating journal entry content."""
        entry = JournalEntry(
            user_id=1,
            title="Original Title",
            content="Original content",
            updated_at=datetime.utcnow() - timedelta(hours=1),
        )

        original_updated_at = entry.updated_at

        entry.update_content("New Title", "New content")

        assert entry.title == "New Title"
        assert entry.content == "New content"
        assert entry.updated_at > original_updated_at

    def test_journal_entry_add_tag(self):
        """Test adding tags to journal entry."""
        entry = JournalEntry(
            user_id=1,
            title="Test Entry",
            content="Content",
            tags=["existing"],
            updated_at=datetime.utcnow() - timedelta(hours=1),
        )

        original_updated_at = entry.updated_at

        # Add new tag
        entry.add_tag("new-tag")
        assert "new-tag" in entry.tags
        assert "existing" in entry.tags
        assert entry.updated_at > original_updated_at

        # Try to add duplicate tag
        entry.add_tag("new-tag")
        assert entry.tags.count("new-tag") == 1

        # Try to add empty tag
        entry.add_tag("")
        assert "" not in entry.tags

    def test_journal_entry_remove_tag(self):
        """Test removing tags from journal entry."""
        entry = JournalEntry(
            user_id=1,
            title="Test Entry",
            content="Content",
            tags=["tag1", "tag2", "tag3"],
            updated_at=datetime.utcnow() - timedelta(hours=1),
        )

        original_updated_at = entry.updated_at

        # Remove existing tag
        entry.remove_tag("tag2")
        assert "tag2" not in entry.tags
        assert "tag1" in entry.tags
        assert "tag3" in entry.tags
        assert entry.updated_at > original_updated_at

        # Try to remove non-existent tag
        entry.remove_tag("nonexistent")
        # Should not raise error

    def test_journal_entry_set_mood(self):
        """Test setting mood rating."""
        entry = JournalEntry(
            user_id=1,
            title="Test Entry",
            content="Content",
            updated_at=datetime.utcnow() - timedelta(hours=1),
        )

        original_updated_at = entry.updated_at

        # Set valid mood
        entry.set_mood(7)
        assert entry.mood == 7
        assert entry.updated_at > original_updated_at

        # Set invalid mood
        with pytest.raises(ValueError, match="Mood rating must be between 1 and 10"):
            entry.set_mood(0)

        with pytest.raises(ValueError, match="Mood rating must be between 1 and 10"):
            entry.set_mood(11)

    def test_journal_entry_to_dict(self):
        """Test converting journal entry to dictionary."""
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()

        entry = JournalEntry(
            entry_id="test-id",
            user_id=1,
            title="Test Entry",
            content="Test content",
            entry_type=EntryType.WEEKLY,
            mood=6,
            tags=["tag1", "tag2"],
            related_quest_id="quest-123",
            related_achievement_id="achievement-456",
            created_at=created_at,
            updated_at=updated_at,
        )

        result = entry.to_dict()

        assert result["entry_id"] == "test-id"
        assert result["user_id"] == 1
        assert result["title"] == "Test Entry"
        assert result["content"] == "Test content"
        assert result["entry_type"] == "weekly"
        assert result["mood"] == 6
        assert result["tags"] == ["tag1", "tag2"]
        assert result["related_quest_id"] == "quest-123"
        assert result["related_achievement_id"] == "achievement-456"
        assert result["created_at"] == created_at.isoformat()
        assert result["updated_at"] == updated_at.isoformat()

    def test_journal_entry_to_dict_with_none_values(self):
        """Test converting journal entry to dictionary with None values."""
        entry = JournalEntry(user_id=1, title="Test Entry", content="Test content")

        result = entry.to_dict()

        assert result["mood"] is None
        assert result["related_quest_id"] is None
        assert result["related_achievement_id"] is None
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_journal_entry_entry_types(self):
        """Test different entry types."""
        for entry_type in EntryType:
            entry = JournalEntry(
                user_id=1, title="Test Entry", content="Content", entry_type=entry_type
            )
            assert entry.entry_type == entry_type

    def test_journal_entry_related_items(self):
        """Test setting related quest and achievement IDs."""
        entry = JournalEntry(
            user_id=1,
            title="Test Entry",
            content="Content",
            related_quest_id="quest-123",
            related_achievement_id="achievement-456",
        )

        assert entry.related_quest_id == "quest-123"
        assert entry.related_achievement_id == "achievement-456"
