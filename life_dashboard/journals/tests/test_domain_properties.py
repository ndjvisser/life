"""
Property-based tests for journals domain - using Hypothesis for comprehensive validation.
"""

from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("hypothesis")
from hypothesis import assume, given
from hypothesis import strategies as st

from life_dashboard.journals.domain.entities import JournalEntry
from life_dashboard.journals.domain.value_objects import (
    EntryContent,
    EntryId,
    EntryTitle,
    MoodRating,
    Tag,
    UserId,
)


@pytest.mark.property
@pytest.mark.domain
class TestJournalEntryProperties:
    """Property-based tests for JournalEntry entity."""

    @given(
        user_id=st.integers(min_value=1, max_value=1000000),
        title=st.text(min_size=1, max_size=200),
        content=st.text(max_size=10000),
        mood=st.one_of(st.none(), st.integers(min_value=1, max_value=10)),
    )
    def test_journal_entry_creation_always_valid_with_valid_inputs(
        self, user_id, title, content, mood
    ):
        """Test that JournalEntry creation always succeeds with valid inputs."""
        # Filter out problematic characters that might cause issues
        assume(title.strip())  # Ensure title is not just whitespace

        entry = JournalEntry(
            user_id=user_id, title=title.strip(), content=content, mood=mood
        )

        assert entry.user_id == user_id
        assert entry.title == title.strip()
        assert entry.content == content
        assert entry.mood == mood
        assert entry.entry_id is not None

    @given(mood=st.integers(min_value=1, max_value=10))
    def test_journal_entry_mood_setting_always_valid(self, mood):
        """Test that setting valid mood always succeeds."""
        entry = JournalEntry(user_id=1, title="Test Entry", content="Content")

        entry.set_mood(mood)
        assert entry.mood == mood
        assert 1 <= entry.mood <= 10

    @given(
        tags=st.lists(
            st.text(min_size=1, max_size=50).filter(
                lambda x: x.replace("-", "").replace("_", "").isalnum()
            ),
            max_size=10,
        )
    )
    def test_journal_entry_tag_operations_maintain_invariants(self, tags):
        """Test that tag operations maintain invariants."""
        entry = JournalEntry(user_id=1, title="Test Entry", content="Content")

        # Add all tags
        for tag in tags:
            if tag:  # Skip empty tags
                entry.add_tag(tag)

        # Verify no duplicates
        assert len(entry.tags) == len(set(entry.tags))

        # Verify all added tags are present
        for tag in tags:
            if tag:
                assert tag in entry.tags

    @given(title=st.text(min_size=1, max_size=200), content=st.text(max_size=10000))
    def test_journal_entry_update_content_always_updates_timestamp(
        self, title, content
    ):
        """Test that updating content always updates the timestamp."""
        assume(title.strip())  # Ensure title is not just whitespace

        entry = JournalEntry(
            user_id=1,
            title="Original Title",
            content="Original content",
            updated_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        original_updated_at = entry.updated_at

        entry.update_content(title.strip(), content)

        assert entry.title == title.strip()
        assert entry.content == content
        assert entry.updated_at > original_updated_at


@pytest.mark.property
@pytest.mark.domain
class TestValueObjectProperties:
    """Property-based tests for value objects."""

    @given(entry_id=st.text(min_size=1, max_size=100))
    def test_entry_id_accepts_valid_strings(self, entry_id):
        """Test that EntryId accepts valid strings."""
        entry_id_vo = EntryId(entry_id)
        assert entry_id_vo.value == entry_id

    @given(entry_id=st.text(min_size=101))
    def test_entry_id_rejects_long_strings(self, entry_id):
        """Test that EntryId rejects strings that are too long."""
        with pytest.raises(ValueError, match="Entry ID cannot exceed 100 characters"):
            EntryId(entry_id)

    @given(title=st.text(min_size=1, max_size=200))
    def test_entry_title_accepts_valid_strings(self, title):
        """Test that EntryTitle accepts valid strings."""
        title_vo = EntryTitle(title)
        assert title_vo.value == title

    @given(title=st.text(min_size=201))
    def test_entry_title_rejects_long_strings(self, title):
        """Test that EntryTitle rejects strings that are too long."""
        with pytest.raises(
            ValueError, match="Entry title cannot exceed 200 characters"
        ):
            EntryTitle(title)

    @given(content=st.text(max_size=10000))
    def test_entry_content_accepts_valid_strings(self, content):
        """Test that EntryContent accepts valid strings."""
        content_vo = EntryContent(content)
        assert content_vo.value == content
        assert content_vo.word_count() >= 0
        assert content_vo.character_count() == len(content)

    def test_entry_content_rejects_long_strings(self):
        """Test that EntryContent rejects strings that are too long."""
        long_content = "x" * 10001
        with pytest.raises(
            ValueError, match="Entry content cannot exceed 10,000 characters"
        ):
            EntryContent(long_content)

    @given(mood=st.integers(min_value=1, max_value=10))
    def test_mood_rating_accepts_valid_range(self, mood):
        """Test that MoodRating accepts valid range."""
        mood_vo = MoodRating(mood)
        assert mood_vo.value == mood

        # Test mood categorization
        if mood >= 6:
            assert mood_vo.is_positive()
            assert not mood_vo.is_negative()
            assert not mood_vo.is_neutral()
        elif mood <= 4:
            assert mood_vo.is_negative()
            assert not mood_vo.is_positive()
            assert not mood_vo.is_neutral()
        else:  # mood == 5
            assert mood_vo.is_neutral()
            assert not mood_vo.is_positive()
            assert not mood_vo.is_negative()

    @given(mood=st.integers().filter(lambda x: x < 1 or x > 10))
    def test_mood_rating_rejects_invalid_range(self, mood):
        """Test that MoodRating rejects invalid range."""
        with pytest.raises(ValueError, match="Mood rating must be between 1 and 10"):
            MoodRating(mood)

    @given(
        tag=st.text(min_size=1, max_size=50).filter(
            lambda x: x.replace("-", "").replace("_", "").isalnum()
        )
    )
    def test_tag_accepts_valid_strings(self, tag):
        """Test that Tag accepts valid strings."""
        tag_vo = Tag(tag)
        assert tag_vo.value == tag
        assert tag_vo.normalized() == tag.lower().strip()

    def test_tag_rejects_long_strings(self):
        """Test that Tag rejects strings that are too long."""
        long_tag = "a" * 51
        with pytest.raises(ValueError, match="Tag cannot exceed 50 characters"):
            Tag(long_tag)

    @given(user_id=st.integers(min_value=1, max_value=2**31 - 1))
    def test_user_id_accepts_positive_integers(self, user_id):
        """Test that UserId accepts positive integers."""
        user_id_vo = UserId(user_id)
        assert user_id_vo.value == user_id

    @given(user_id=st.integers(max_value=0))
    def test_user_id_rejects_non_positive_integers(self, user_id):
        """Test that UserId rejects non-positive integers."""
        with pytest.raises(ValueError, match="User ID must be positive"):
            UserId(user_id)
