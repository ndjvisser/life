"""
Tests for unlock_next_quests user ID fix.
"""

from unittest.mock import MagicMock

import pytest

from life_dashboard.quests.application.services import QuestChainService
from life_dashboard.quests.domain.entities import Quest, QuestStatus


class TestUnlockNextQuestsFix:
    """Test cases for unlock_next_quests user ID fix."""

    def setup_method(self):
        """Set up test dependencies."""
        self.quest_repo = MagicMock()
        self.quest_service = QuestChainService(self.quest_repo)

    def test_unlock_next_quests_fetches_correct_user_id(self):
        """Test that unlock_next_quests fetches user ID from completed quest instead of using hardcoded 0."""
        # Arrange
        completed_quest = MagicMock(spec=Quest)
        completed_quest.user_id = 123
        completed_quest.quest_id = "completed_quest"

        draft_quest = MagicMock(spec=Quest)
        draft_quest.quest_id = "draft_quest"
        draft_quest.prerequisite_quest_ids = ["completed_quest"]
        draft_quest.status = QuestStatus.DRAFT

        self.quest_repo.get_by_id.return_value = completed_quest
        self.quest_repo.get_by_user_id.return_value = [draft_quest]
        self.quest_repo.save.return_value = draft_quest
        self.quest_service.check_prerequisites = MagicMock(return_value=True)

        # Act
        result = self.quest_service.unlock_next_quests("completed_quest")

        # Assert
        # Should fetch the completed quest first
        self.quest_repo.get_by_id.assert_called_once_with("completed_quest")

        # Should fetch quests for the correct user (not 0)
        self.quest_repo.get_by_user_id.assert_called_once_with(123)

        # Should unlock the draft quest
        assert len(result) == 1
        assert draft_quest.status == QuestStatus.ACTIVE

    def test_unlock_next_quests_handles_missing_completed_quest(self):
        """Test that unlock_next_quests raises ValueError when completed quest is not found."""
        # Arrange
        self.quest_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            self.quest_service.unlock_next_quests("nonexistent_quest")

        # Should not call get_by_user_id if completed quest is not found
        self.quest_repo.get_by_user_id.assert_not_called()

    def test_unlock_next_quests_preserves_filtering_logic(self):
        """Test that unlock_next_quests preserves existing filtering logic for DRAFT status and prerequisites."""
        # Arrange
        completed_quest = MagicMock(spec=Quest)
        completed_quest.user_id = 456

        # Quest that should be unlocked
        valid_quest = MagicMock(spec=Quest)
        valid_quest.quest_id = "valid_quest"
        valid_quest.prerequisite_quest_ids = ["completed_quest"]
        valid_quest.status = QuestStatus.DRAFT

        # Quest with wrong prerequisite
        wrong_prereq_quest = MagicMock(spec=Quest)
        wrong_prereq_quest.quest_id = "wrong_prereq"
        wrong_prereq_quest.prerequisite_quest_ids = ["other_quest"]
        wrong_prereq_quest.status = QuestStatus.DRAFT

        # Quest with wrong status
        wrong_status_quest = MagicMock(spec=Quest)
        wrong_status_quest.quest_id = "wrong_status"
        wrong_status_quest.prerequisite_quest_ids = ["completed_quest"]
        wrong_status_quest.status = QuestStatus.ACTIVE

        user_quests = [valid_quest, wrong_prereq_quest, wrong_status_quest]

        self.quest_repo.get_by_id.return_value = completed_quest
        self.quest_repo.get_by_user_id.return_value = user_quests
        self.quest_repo.save.return_value = valid_quest
        self.quest_service.check_prerequisites = MagicMock(return_value=True)

        # Act
        result = self.quest_service.unlock_next_quests("completed_quest")

        # Assert
        # Only the valid quest should be unlocked
        assert len(result) == 1
        assert result[0] == valid_quest
        assert valid_quest.status == QuestStatus.ACTIVE

        # check_prerequisites should only be called for the valid quest
        self.quest_service.check_prerequisites.assert_called_once_with("valid_quest")

    def test_unlock_next_quests_returns_empty_list_when_no_quests_to_unlock(self):
        """Test that unlock_next_quests returns empty list when no quests match criteria."""
        # Arrange
        completed_quest = MagicMock(spec=Quest)
        completed_quest.user_id = 789

        # No quests have the completed quest as prerequisite
        unrelated_quest = MagicMock(spec=Quest)
        unrelated_quest.prerequisite_quest_ids = ["other_quest"]
        unrelated_quest.status = QuestStatus.DRAFT

        self.quest_repo.get_by_id.return_value = completed_quest
        self.quest_repo.get_by_user_id.return_value = [unrelated_quest]

        # Act
        result = self.quest_service.unlock_next_quests("completed_quest")

        # Assert
        assert len(result) == 0
        self.quest_repo.save.assert_not_called()
