"""
Contract tests for journals services - validating service layer APIs with Pydantic.
"""

from datetime import datetime

import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel, ConfigDict, Field

from life_dashboard.journals.domain.entities import EntryType, JournalEntry
from life_dashboard.journals.domain.repositories import JournalEntryRepository
from life_dashboard.journals.domain.services import JournalService
from life_dashboard.journals.domain.value_objects import EntryId, UserId


# Pydantic contracts for service responses
class JournalEntryResponse(BaseModel):
    """Contract for journal entry responses."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str
    user_id: int
    title: str
    content: str
    entry_type: str
    mood: int | None = None
    tags: list[str] = Field(default_factory=list)
    related_quest_id: str | None = None
    related_achievement_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class MoodStatisticsResponse(BaseModel):
    """Contract for mood statistics responses."""

    model_config = ConfigDict(extra="forbid")

    average_mood: float | None
    mood_count: int
    positive_days: int
    negative_days: int
    neutral_days: int


class CreateEntryRequest(BaseModel):
    """Contract for create entry requests."""

    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(max_length=10000)
    entry_type: str = "daily"
    mood: int | None = Field(None, ge=1, le=10)
    tags: list[str] | None = None
    related_quest_id: str | None = None
    related_achievement_id: str | None = None


class UpdateEntryRequest(BaseModel):
    """Contract for update entry requests."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str = Field(min_length=1)
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, max_length=10000)
    mood: int | None = Field(None, ge=1, le=10)
    tags: list[str] | None = None


# Mock repository for testing
class MockJournalEntryRepository(JournalEntryRepository):
    """Mock repository for testing."""

    def __init__(self):
        self.entries = {}
        self.next_id = 1

    def save(self, entry: JournalEntry) -> JournalEntry:
        if not entry.entry_id:
            entry.entry_id = str(self.next_id)
            self.next_id += 1
        self.entries[entry.entry_id] = entry
        return entry

    def get_by_id(self, entry_id: EntryId) -> JournalEntry | None:
        return self.entries.get(entry_id.value)

    def get_by_user(self, user_id: UserId) -> list[JournalEntry]:
        return [
            entry for entry in self.entries.values() if entry.user_id == user_id.value
        ]

    def get_by_user_and_date_range(
        self, user_id: UserId, start_date: datetime, end_date: datetime
    ) -> list[JournalEntry]:
        return [
            entry
            for entry in self.entries.values()
            if entry.user_id == user_id.value
            and entry.created_at
            and start_date <= entry.created_at <= end_date
        ]

    def delete(self, entry_id: EntryId) -> bool:
        if entry_id.value in self.entries:
            del self.entries[entry_id.value]
            return True
        return False

    def search_by_content(self, user_id: UserId, query: str) -> list[JournalEntry]:
        return [
            entry
            for entry in self.entries.values()
            if entry.user_id == user_id.value
            and (
                query.lower() in entry.title.lower()
                or query.lower() in entry.content.lower()
            )
        ]

    def get_by_tags(self, user_id: UserId, tags: list[str]) -> list[JournalEntry]:
        return [
            entry
            for entry in self.entries.values()
            if entry.user_id == user_id.value and any(tag in entry.tags for tag in tags)
        ]


@pytest.mark.contract
@pytest.mark.unit
class TestJournalServiceContracts:
    """Test journal service contracts."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = MockJournalEntryRepository()
        self.service = JournalService(self.repository)

    def test_create_entry_contract_validation(self):
        """Test create entry request contract validation."""
        # Valid request
        valid_request = CreateEntryRequest(
            user_id=1,
            title="Test Entry",
            content="Test content",
            mood=7,
            tags=["test", "contract"],
        )

        assert valid_request.user_id == 1
        assert valid_request.title == "Test Entry"
        assert valid_request.mood == 7

        # Invalid request - missing title
        with pytest.raises(ValueError):
            CreateEntryRequest(user_id=1, title="", content="Test content")

        # Invalid request - invalid mood
        with pytest.raises(ValueError):
            CreateEntryRequest(
                user_id=1, title="Test Entry", content="Test content", mood=11
            )

    def test_update_entry_contract_validation(self):
        """Test update entry request contract validation."""
        # Valid request
        valid_request = UpdateEntryRequest(
            entry_id="test-id", title="Updated Title", mood=5
        )

        assert valid_request.entry_id == "test-id"
        assert valid_request.title == "Updated Title"
        assert valid_request.mood == 5

        # Invalid request - empty entry_id
        with pytest.raises(ValueError):
            UpdateEntryRequest(entry_id="", title="Updated Title")

    def test_journal_service_create_returns_valid_response(self):
        """Test that journal service create returns valid response contract."""
        entry = self.service.create_entry(
            user_id=1,
            title="Test Entry",
            content="Test content",
            entry_type=EntryType.DAILY,
            mood=8,
            tags=["test", "contract"],
        )

        # Convert to dict and validate against contract
        entry_dict = entry.to_dict()
        response = JournalEntryResponse(**entry_dict)

        assert response.user_id == 1
        assert response.title == "Test Entry"
        assert response.content == "Test content"
        assert response.entry_type == "daily"
        assert response.mood == 8
        assert response.tags == ["test", "contract"]

    def test_journal_service_update_returns_valid_response(self):
        """Test that journal service update returns valid response contract."""
        # Create entry first
        entry = self.service.create_entry(
            user_id=1, title="Original Title", content="Original content"
        )

        # Update entry
        updated_entry = self.service.update_entry(
            entry_id=entry.entry_id, title="Updated Title", mood=6
        )

        # Validate response contract
        entry_dict = updated_entry.to_dict()
        response = JournalEntryResponse(**entry_dict)

        assert response.title == "Updated Title"
        assert response.mood == 6

    def test_mood_statistics_returns_valid_response(self):
        """Test that mood statistics returns valid response contract."""
        # Create entries with moods
        self.service.create_entry(user_id=1, title="Entry 1", content="Content", mood=8)
        self.service.create_entry(user_id=1, title="Entry 2", content="Content", mood=4)
        self.service.create_entry(user_id=1, title="Entry 3", content="Content", mood=5)

        stats = self.service.get_mood_statistics(user_id=1, days=30)

        # Validate against contract
        response = MoodStatisticsResponse(**stats)

        assert response.mood_count == 3
        assert response.positive_days == 1
        assert response.negative_days == 1
        assert response.neutral_days == 1
        assert response.average_mood is not None

    def test_contract_schema_examples_are_valid(self):
        """Test that contract schema examples are valid."""
        # Test JournalEntryResponse schema
        example_entry = {
            "entry_id": "test-123",
            "user_id": 1,
            "title": "Example Entry",
            "content": "Example content",
            "entry_type": "daily",
            "mood": 7,
            "tags": ["example", "test"],
            "related_quest_id": None,
            "related_achievement_id": None,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00",
        }

        response = JournalEntryResponse(**example_entry)
        assert response.entry_id == "test-123"
        assert response.user_id == 1

        # Test MoodStatisticsResponse schema
        example_stats = {
            "average_mood": 6.5,
            "mood_count": 10,
            "positive_days": 6,
            "negative_days": 2,
            "neutral_days": 2,
        }

        stats_response = MoodStatisticsResponse(**example_stats)
        assert stats_response.average_mood == 6.5
        assert stats_response.mood_count == 10
