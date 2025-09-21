"""
Snapshot tests for journals API responses - preventing breaking changes.
"""

import pytest

pytest.importorskip("pytest_snapshot")

from life_dashboard.journals.domain.entities import EntryType
from life_dashboard.journals.domain.services import JournalService
from life_dashboard.journals.tests.test_service_contracts import (
    MockJournalEntryRepository,
)
from tests.snapshot_utils import assert_json_snapshot


@pytest.mark.snapshot
@pytest.mark.unit
class TestJournalAPISnapshots:
    """Test journal API response snapshots."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = MockJournalEntryRepository()
        self.service = JournalService(self.repository)

    def test_journal_entry_creation_response_snapshot(self, snapshot):
        """Test journal entry creation response structure."""
        entry = self.service.create_entry(
            user_id=1,
            title="My Daily Reflection",
            content="Today was productive. I completed my morning routine and worked on my goals.",
            entry_type=EntryType.DAILY,
            mood=8,
            tags=["productivity", "goals", "morning-routine"],
            related_quest_id="quest-123",
            related_achievement_id="achievement-456",
        )

        # Create predictable response data
        response_data = entry.to_dict()
        # Replace dynamic values with predictable ones for snapshot
        response_data["entry_id"] = "entry-123"
        response_data["created_at"] = "2023-01-01T12:00:00.000000"
        response_data["updated_at"] = "2023-01-01T12:00:00.000000"

        assert_json_snapshot(snapshot, response_data, "journal_entry_creation.json")

    def test_journal_entry_update_response_snapshot(self, snapshot):
        """Test journal entry update response structure."""
        # Create initial entry
        entry = self.service.create_entry(
            user_id=1, title="Original Title", content="Original content", mood=5
        )

        # Update entry
        updated_entry = self.service.update_entry(
            entry_id=entry.entry_id,
            title="Updated Daily Reflection",
            content="Updated content with more details about my progress.",
            mood=9,
            tags=["updated", "progress", "reflection"],
        )

        # Create predictable response data
        response_data = updated_entry.to_dict()
        response_data["entry_id"] = "entry-123"
        response_data["created_at"] = "2023-01-01T12:00:00.000000"
        response_data["updated_at"] = "2023-01-01T13:00:00.000000"

        assert_json_snapshot(snapshot, response_data, "journal_entry_update.json")

    def test_mood_statistics_response_snapshot(self, snapshot):
        """Test mood statistics response structure."""
        # Create entries with various moods
        entries_data = [
            {"title": "Great Day", "mood": 9, "tags": ["positive", "productive"]},
            {"title": "Okay Day", "mood": 6, "tags": ["neutral", "steady"]},
            {"title": "Tough Day", "mood": 3, "tags": ["challenging", "growth"]},
            {"title": "Amazing Day", "mood": 10, "tags": ["excellent", "breakthrough"]},
            {"title": "Average Day", "mood": 5, "tags": ["neutral", "routine"]},
        ]

        for entry_data in entries_data:
            self.service.create_entry(
                user_id=1,
                title=entry_data["title"],
                content=f"Content for {entry_data['title']}",
                mood=entry_data["mood"],
                tags=entry_data["tags"],
            )

        stats = self.service.get_mood_statistics(user_id=1, days=30)

        # Round average_mood for consistent snapshots
        if stats["average_mood"] is not None:
            stats["average_mood"] = round(stats["average_mood"], 2)

        assert_json_snapshot(snapshot, stats, "mood_statistics.json")

    def test_journal_entries_list_response_snapshot(self, snapshot):
        """Test journal entries list response structure."""
        # Create multiple entries
        entries_data = [
            {
                "title": "Morning Reflection",
                "content": "Started the day with meditation and planning.",
                "entry_type": EntryType.DAILY,
                "mood": 7,
                "tags": ["morning", "meditation", "planning"],
            },
            {
                "title": "Weekly Review",
                "content": "Reviewing the week's accomplishments and areas for improvement.",
                "entry_type": EntryType.WEEKLY,
                "mood": 8,
                "tags": ["review", "accomplishments", "improvement"],
            },
            {
                "title": "Milestone Achievement",
                "content": "Reached my fitness goal for the month!",
                "entry_type": EntryType.MILESTONE,
                "mood": 10,
                "tags": ["milestone", "fitness", "achievement"],
            },
        ]

        created_entries = []
        for _i, entry_data in enumerate(entries_data):
            entry = self.service.create_entry(
                user_id=1,
                title=entry_data["title"],
                content=entry_data["content"],
                entry_type=entry_data["entry_type"],
                mood=entry_data["mood"],
                tags=entry_data["tags"],
            )
            created_entries.append(entry)

        # Get all entries for user
        user_entries = self.service.get_user_entries(user_id=1)

        # Create predictable response data
        response_data = []
        for i, entry in enumerate(user_entries):
            entry_dict = entry.to_dict()
            entry_dict["entry_id"] = f"entry-{i + 1}"
            entry_dict["created_at"] = f"2023-01-0{i + 1}T12:00:00.000000"
            entry_dict["updated_at"] = f"2023-01-0{i + 1}T12:00:00.000000"
            response_data.append(entry_dict)

        # Sort by entry_id for consistent ordering
        response_data.sort(key=lambda x: x["entry_id"])

        assert_json_snapshot(snapshot, response_data, "journal_entries_list.json")

    def test_journal_entry_search_response_snapshot(self, snapshot):
        """Test journal entry search response structure."""
        # Create entries with searchable content
        search_entries = [
            {
                "title": "Productivity Tips",
                "content": "Today I learned about time management and productivity techniques.",
            },
            {
                "title": "Fitness Journey",
                "content": "Made progress on my fitness goals with a great workout.",
            },
            {
                "title": "Learning Goals",
                "content": "Focused on learning new productivity skills and techniques.",
            },
            {
                "title": "Daily Routine",
                "content": "Established a better morning routine for increased productivity.",
            },
        ]

        for entry_data in search_entries:
            self.service.create_entry(
                user_id=1,
                title=entry_data["title"],
                content=entry_data["content"],
                mood=7,
            )

        # Search for entries containing "productivity"
        search_results = self.service.search_entries(user_id=1, query="productivity")

        # Create predictable response data
        response_data = []
        for i, entry in enumerate(search_results):
            entry_dict = entry.to_dict()
            entry_dict["entry_id"] = f"search-result-{i + 1}"
            entry_dict["created_at"] = "2023-01-01T12:00:00.000000"
            entry_dict["updated_at"] = "2023-01-01T12:00:00.000000"
            response_data.append(entry_dict)

        # Sort by title for consistent ordering
        response_data.sort(key=lambda x: x["title"])

        assert_json_snapshot(snapshot, response_data, "journal_search_results.json")
