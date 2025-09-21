"""Tests for QuestChainService child quest creation sanitization."""

from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from life_dashboard.quests.application.services import QuestChainService
from life_dashboard.quests.domain.entities import (
    QuestDifficulty,
    QuestStatus,
    QuestType,
)


class TestQuestChainService:
    """Test suite for QuestChainService create_quest_chain sanitization."""

    def setup_method(self):
        """Set up a QuestChainService instance with a mocked repository."""

        self.quest_repo = MagicMock()
        self.quest_repo.create.side_effect = lambda quest: quest
        self.service = QuestChainService(self.quest_repo)

    def test_create_quest_chain_sanitizes_and_normalizes_child_data(
        self, monkeypatch
    ) -> None:
        """Quest data is sanitized and normalized before persistence."""

        fixed_now = datetime(2024, 1, 1, 12, 0, 0)

        class FixedDateTime(datetime):
            @classmethod
            def utcnow(cls):  # pragma: no cover - trivial override
                return fixed_now

        monkeypatch.setattr(
            "life_dashboard.quests.application.services.datetime",
            FixedDateTime,
        )

        child_quests = [
            {
                "quest_id": "123",
                "title": "  Quest Title  ",
                "description": "desc",
                "quest_type": "side",
                "difficulty": "hard",
                "status": "completed",
                "experience_reward": "50",
                "completion_percentage": "42.5",
                "start_date": "2024-02-01",
                "due_date": "2024-02-10",
                "completed_at": "2024-02-11T00:00:00",
                "prerequisite_quest_ids": ("pre-1", "pre-2"),
                # Disallowed keys should be ignored.
                "user_id": 999,
                "parent_quest_id": "should-remove",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            }
        ]

        created = self.service.create_quest_chain(1, "parent-1", child_quests)

        assert len(created) == 1
        quest = created[0]

        assert quest.user_id.value == 1
        assert quest.parent_quest_id == "parent-1"
        assert quest.quest_id is not None
        assert quest.quest_id.value == 123
        assert quest.title.value == "Quest Title"
        assert quest.description.value == "desc"
        assert quest.quest_type == QuestType.SIDE
        assert quest.difficulty == QuestDifficulty.HARD
        assert quest.status == QuestStatus.COMPLETED
        assert quest.experience_reward.value == 50
        assert quest.progress == pytest.approx(42.5)
        assert quest.start_date == date(2024, 2, 1)
        assert quest.due_date == date(2024, 2, 10)
        assert quest.completed_at == datetime(2024, 2, 11, 0, 0)
        assert quest.prerequisite_quest_ids == ["pre-1", "pre-2"]
        assert quest.created_at == fixed_now
        assert quest.updated_at == fixed_now

        self.quest_repo.create.assert_called_once()

    def test_create_quest_chain_missing_title_raises_value_error(self) -> None:
        """A missing title should raise a ValueError before persistence."""

        child_quests = [
            {
                "quest_id": "123",
                "experience_reward": 10,
            }
        ]

        with pytest.raises(ValueError):
            self.service.create_quest_chain(1, "parent-1", child_quests)

        self.quest_repo.create.assert_not_called()

    def test_create_quest_chain_invalid_difficulty_raises_value_error(self) -> None:
        """Invalid difficulty values should be rejected."""

        child_quests = [
            {
                "quest_id": "123",
                "title": "Quest Title",
                "experience_reward": 10,
                "difficulty": "impossible",
            }
        ]

        with pytest.raises(ValueError):
            self.service.create_quest_chain(1, "parent-1", child_quests)

        self.quest_repo.create.assert_not_called()
