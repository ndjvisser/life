"""
Tests for quest status default fix and domain-DB alignment.

This test suite verifies that the quest status mismatch between domain
expectations (DRAFT) and DB defaults has been properly fixed.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from life_dashboard.quests.domain.entities import Quest as DomainQuest
from life_dashboard.quests.domain.entities import (
    QuestDifficulty,
    QuestStatus,
    QuestType,
)
from life_dashboard.quests.models import Quest as DjangoQuest


class TestQuestStatusFix(TestCase):
    """Test cases for quest status default fix and domain-DB alignment."""

    def setUp(self):
        """Set up test data."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="queststatustest",
            email="queststatus@test.com",
            password="testpass123",
        )

    def test_db_model_defaults_to_draft_status(self):
        """Test that new DB quests default to 'draft' status."""
        django_quest = DjangoQuest.objects.create(
            user=self.user,
            title="Test Quest",
            description="Test Description",
            difficulty="medium",
            quest_type="main",
            experience_reward=50,
        )

        self.assertEqual(django_quest.status, "draft")

    def test_status_choices_completeness(self):
        """Test that STATUS_CHOICES includes all domain status values."""
        status_choices = dict(DjangoQuest.STATUS_CHOICES)
        expected_statuses = ["draft", "active", "completed", "failed", "paused"]

        for status in expected_statuses:
            self.assertIn(status, status_choices, f"STATUS_CHOICES missing '{status}'")

        # Verify the display names are reasonable
        self.assertEqual(status_choices["draft"], "Draft")
        self.assertEqual(status_choices["active"], "Active")
        self.assertEqual(status_choices["completed"], "Completed")
        self.assertEqual(status_choices["failed"], "Failed")
        self.assertEqual(status_choices["paused"], "Paused")

    def test_domain_entity_with_draft_status(self):
        """Test that domain entity can be created with DRAFT status."""
        domain_quest = DomainQuest(
            user_id=self.user.id,
            title="Domain Test Quest",
            description="Domain Test Description",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.MEDIUM,
            status=QuestStatus.DRAFT,
            experience_reward=75,
        )

        self.assertEqual(domain_quest.status, QuestStatus.DRAFT)

    def test_start_quest_with_draft_status(self):
        """Test that start_quest works correctly with DRAFT status."""
        draft_quest = DomainQuest(
            user_id=self.user.id,
            title="Draft Quest",
            description="Quest to be started",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.EASY,
            status=QuestStatus.DRAFT,
            experience_reward=25,
        )

        # This should work without raising an exception
        draft_quest.start_quest()

        self.assertEqual(draft_quest.status, QuestStatus.ACTIVE)
        self.assertIsNotNone(draft_quest.start_date)

    def test_start_quest_error_handling(self):
        """Test that start_quest raises ValueError for non-DRAFT status."""
        active_quest = DomainQuest(
            user_id=self.user.id,
            title="Active Quest",
            description="Already active quest",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.MEDIUM,
            status=QuestStatus.ACTIVE,
            experience_reward=50,
        )

        with self.assertRaises(ValueError) as context:
            active_quest.start_quest()

        self.assertIn("Cannot start quest in active status", str(context.exception))

    def test_db_validation_with_all_status_values(self):
        """Test that all status values pass Django model validation."""
        test_statuses = ["draft", "active", "completed", "failed", "paused"]

        for status in test_statuses:
            quest = DjangoQuest(
                user=self.user,
                title=f"Test {status.title()} Quest",
                description=f"Testing {status} status",
                status=status,
                experience_reward=10,
            )

            # Should not raise ValidationError
            try:
                quest.full_clean()
            except ValidationError:
                self.fail(f"Status '{status}' failed validation")

    def test_invalid_status_raises_validation_error(self):
        """Test that invalid status values raise ValidationError."""
        quest = DjangoQuest(
            user=self.user,
            title="Invalid Status Quest",
            description="Testing invalid status",
            status="invalid_status",
            experience_reward=10,
        )

        with self.assertRaises(ValidationError):
            quest.full_clean()

    def test_domain_db_alignment(self):
        """Test that domain-DB alignment allows proper quest lifecycle."""
        # Create quest in DB (defaults to draft)
        db_quest = DjangoQuest.objects.create(
            user=self.user,
            title="Alignment Test Quest",
            description="Testing domain-DB alignment",
            experience_reward=100,
        )

        # Verify it defaults to draft
        self.assertEqual(db_quest.status, "draft")

        # Create corresponding domain entity
        domain_quest = DomainQuest(
            user_id=db_quest.user.id,
            title=db_quest.title,
            description=db_quest.description,
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.MEDIUM,
            status=QuestStatus.DRAFT,  # This should match the DB default
            experience_reward=db_quest.experience_reward,
        )

        # This should work without errors
        domain_quest.start_quest()
        self.assertEqual(domain_quest.status, QuestStatus.ACTIVE)

    def test_quest_lifecycle_progression(self):
        """Test complete quest lifecycle from creation to completion."""
        # Create quest (defaults to DRAFT)
        quest = DomainQuest(
            user_id=self.user.id,
            title="Lifecycle Test Quest",
            description="Testing complete lifecycle",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.MEDIUM,
            status=QuestStatus.DRAFT,
            experience_reward=100,
        )

        # Start quest (DRAFT → ACTIVE)
        quest.start_quest()
        self.assertEqual(quest.status, QuestStatus.ACTIVE)
        self.assertIsNotNone(quest.start_date)

        # Complete quest (ACTIVE → COMPLETED)
        quest.complete_quest()
        self.assertEqual(quest.status, QuestStatus.COMPLETED)
        self.assertIsNotNone(quest.completed_at)

    def test_quest_can_be_paused_and_resumed(self):
        """Test that quest can be paused and resumed."""
        quest = DomainQuest(
            user_id=self.user.id,
            title="Pausable Quest",
            description="Testing pause/resume functionality",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.MEDIUM,
            status=QuestStatus.DRAFT,
            experience_reward=50,
        )

        # Start quest
        quest.start_quest()
        self.assertEqual(quest.status, QuestStatus.ACTIVE)

        # Pause quest
        quest.pause_quest()
        self.assertEqual(quest.status, QuestStatus.PAUSED)

        # Resume quest
        quest.resume_quest()
        self.assertEqual(quest.status, QuestStatus.ACTIVE)

    def test_quest_can_fail(self):
        """Test that quest can be marked as failed."""
        quest = DomainQuest(
            user_id=self.user.id,
            title="Failing Quest",
            description="Testing failure functionality",
            quest_type=QuestType.MAIN,
            difficulty=QuestDifficulty.HARD,
            status=QuestStatus.DRAFT,
            experience_reward=150,
        )

        # Start quest
        quest.start_quest()
        self.assertEqual(quest.status, QuestStatus.ACTIVE)

        # Fail quest
        quest.fail_quest("Test failure reason")
        self.assertEqual(quest.status, QuestStatus.FAILED)
        # Note: The domain entity doesn't store failure reason, just status
