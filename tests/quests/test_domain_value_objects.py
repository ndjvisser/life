"""Tests for quest domain value objects."""

import pytest

from life_dashboard.quests.domain.value_objects import QuestId


def test_quest_id_rejects_boolean_values() -> None:
    with pytest.raises(ValueError):
        QuestId(True)


def test_quest_id_rejects_none_values() -> None:
    with pytest.raises(TypeError):
        QuestId(None)


def test_quest_id_rejects_negative_numeric_string() -> None:
    with pytest.raises(ValueError):
        QuestId(" -10 ")


def test_quest_id_accepts_trimmed_string_identifier() -> None:
    quest_id = QuestId("  quest-abc  ")

    assert quest_id.value == "quest-abc"


def test_quest_id_converts_positive_numeric_string_to_int() -> None:
    quest_id = QuestId(" 42 ")

    assert quest_id.value == 42
