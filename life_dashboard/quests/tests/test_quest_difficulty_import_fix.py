"""
Tests for QuestDifficulty import fix in quests services.
"""

from unittest.mock import MagicMock

from life_dashboard.quests.application.services import QuestService
from life_dashboard.quests.domain.entities import QuestDifficulty, QuestType


class TestQuestDifficultyImportFix:
    """Test cases for QuestDifficulty import and usage fix."""

    def setup_method(self):
        """Set up test dependencies."""
        self.quest_repo = MagicMock()
        self.quest_service = QuestService(self.quest_repo)

    def test_quest_difficulty_import_works(self):
        """Test that QuestDifficulty can be imported correctly."""
        # This test passes if the import in the service file works
        from life_dashboard.quests.domain.entities import QuestDifficulty

        # Verify enum has expected values
        assert QuestDifficulty.EASY.value == "easy"
        assert QuestDifficulty.MEDIUM.value == "medium"
        assert QuestDifficulty.HARD.value == "hard"
        assert QuestDifficulty.LEGENDARY.value == "legendary"

    def test_create_quest_difficulty_mapping(self):
        """Test that create_quest correctly maps difficulty strings to QuestDifficulty enum."""
        # Mock the repository
        mock_quest = MagicMock()
        self.quest_repo.create.return_value = mock_quest

        # Test difficulty mapping
        test_cases = [
            ("easy", QuestDifficulty.EASY),
            ("medium", QuestDifficulty.MEDIUM),
            ("hard", QuestDifficulty.HARD),
            ("legendary", QuestDifficulty.LEGENDARY),
            ("invalid", QuestDifficulty.MEDIUM),  # Should default to MEDIUM
        ]

        for difficulty_str, expected_enum in test_cases:
            # Reset mock
            self.quest_repo.reset_mock()

            # Create quest with difficulty string
            self.quest_service.create_quest(
                user_id=123,
                title="Test Quest",
                description="Test Description",
                quest_type=QuestType.MAIN,
                difficulty=difficulty_str,
                experience_reward=50,
            )

            # Verify repository was called
            self.quest_repo.create.assert_called_once()

            # Get the Quest object that was passed to create
            created_quest = self.quest_repo.create.call_args[0][0]

            # Verify difficulty was mapped correctly
            assert created_quest.difficulty == expected_enum, (
                f"Expected {expected_enum}, got {created_quest.difficulty}"
            )

    def test_quest_difficulty_enum_usage(self):
        """Test that QuestDifficulty enum can be used directly."""
        # Test getattr usage (as used in the service)
        easy_diff = getattr(QuestDifficulty, "EASY", QuestDifficulty.MEDIUM)
        medium_diff = getattr(QuestDifficulty, "MEDIUM", QuestDifficulty.MEDIUM)
        invalid_diff = getattr(QuestDifficulty, "INVALID", QuestDifficulty.MEDIUM)

        assert easy_diff == QuestDifficulty.EASY
        assert medium_diff == QuestDifficulty.MEDIUM
        assert invalid_diff == QuestDifficulty.MEDIUM  # Default fallback

    def test_no_quest_dot_questdifficulty_references(self):
        """Test that there are no remaining Quest.QuestDifficulty references in the service file."""
        # Read the service file
        with open("life_dashboard/quests/application/services.py") as f:
            content = f.read()

        # Should not contain Quest.QuestDifficulty
        assert "Quest.QuestDifficulty" not in content, (
            "Found remaining Quest.QuestDifficulty references"
        )

        # Should contain QuestDifficulty import
        assert "QuestDifficulty," in content or "QuestDifficulty\n" in content, (
            "QuestDifficulty import not found"
        )
