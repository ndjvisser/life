import pytest

from life_dashboard.quests.domain.value_objects import QuestId
from life_dashboard.quests.infrastructure.repositories import _quest_id_as_int


class TestQuestIdNormalization:
    """Tests for quest identifier normalization helper."""

    def test_numeric_quest_id_value_object_returns_int(self):
        """Numeric quest identifiers wrapped in QuestId should resolve to ints."""

        quest_id = QuestId(42)

        assert _quest_id_as_int(quest_id) == 42

    def test_non_numeric_quest_id_value_object_raises_value_error(self):
        """QuestId values containing non-numeric text should raise ValueError."""

        quest_id = QuestId("quest-alpha")

        with pytest.raises(ValueError):
            _quest_id_as_int(quest_id)

    def test_string_with_whitespace_is_trimmed_and_converted(self):
        """String quest identifiers should be trimmed before conversion."""

        assert _quest_id_as_int("   7  ") == 7

    def test_blank_string_raises_value_error(self):
        """Blank string quest identifiers should not be accepted."""

        with pytest.raises(ValueError):
            _quest_id_as_int("   ")
