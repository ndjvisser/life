"""Tests for quests domain value objects."""

from life_dashboard.quests.domain.value_objects import QuestProgress


class TestQuestProgress:
    """Unit tests covering the QuestProgress value object."""

    def test_milestones_converted_to_tuple(self) -> None:
        """QuestProgress should coerce milestone inputs to an immutable tuple."""

        progress = QuestProgress(completion_percentage=10.0, milestones_completed=["start"])

        assert progress.milestones_completed == ("start",)
        assert isinstance(progress.milestones_completed, tuple)

    def test_add_milestone_returns_new_instance(self) -> None:
        """Adding a milestone should return a new QuestProgress instance without mutating the original."""

        progress = QuestProgress(completion_percentage=10.0, milestones_completed=("start",))

        updated = progress.add_milestone("week")

        assert updated is not progress
        assert updated.milestones_completed == ("start", "week")
        assert progress.milestones_completed == ("start",)
        # Adding a duplicate milestone should be a no-op and return the same instance
        assert progress.add_milestone("start") is progress

    def test_update_progress_preserves_milestones(self) -> None:
        """Updating the completion percentage should preserve milestone immutability."""

        progress = QuestProgress(completion_percentage=10.0, milestones_completed=("start",))

        updated = progress.update_progress(55.0)

        assert updated.completion_percentage == 55.0
        assert updated.milestones_completed == ("start",)
        assert isinstance(updated.milestones_completed, tuple)
