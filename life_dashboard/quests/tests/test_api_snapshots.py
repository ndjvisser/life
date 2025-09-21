"""
Snapshot tests for Quest API responses.

These tests capture API response structures to prevent breaking changes.
"""

from datetime import date, datetime
from unittest.mock import Mock

import pytest

pytest.importorskip("pytest_snapshot")

from tests.snapshot_utils import assert_json_snapshot

from life_dashboard.quests.domain.entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestDifficulty,
    QuestStatus,
    QuestType,
)
from life_dashboard.quests.domain.services import HabitService, QuestService
from life_dashboard.quests.domain.value_objects import (
    CompletionCount,
    ExperienceReward,
    HabitId,
    HabitName,
    QuestDescription,
    QuestId,
    QuestTitle,
    StreakCount,
    UserId,
)


class TestQuestAPISnapshots:
    """Snapshot tests for Quest API responses"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_repository = Mock()
        self.quest_service = QuestService(self.mock_repository)

    def test_quest_creation_response_snapshot(self, snapshot):
        """Test quest creation API response structure"""
        # Mock repository response
        mock_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python Programming"),
            description=QuestDescription(
                "Complete comprehensive Python tutorial with hands-on projects"
            ),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.DRAFT,
            experience_reward=ExperienceReward(150),
            start_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        self.mock_repository.save.return_value = mock_quest

        # Create quest through service
        result = self.quest_service.create_quest(
            user_id=UserId(1),
            title="Learn Python Programming",
            description="Complete comprehensive Python tutorial with hands-on projects",
            difficulty="medium",
            quest_type="main",
            experience_reward=150,
            start_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
        )

        # Convert to API response format
        api_response = {
            "quest_id": result.quest_id.value,
            "user_id": result.user_id.value,
            "title": result.title.value,
            "description": result.description.value,
            "difficulty": result.difficulty.value,
            "quest_type": result.quest_type.value,
            "status": result.status.value,
            "experience_reward": result.experience_reward.value,
            "start_date": result.start_date.isoformat() if result.start_date else None,
            "due_date": result.due_date.isoformat() if result.due_date else None,
            "completed_at": result.completed_at.isoformat()
            if result.completed_at
            else None,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat(),
            "difficulty_multiplier": result.get_difficulty_multiplier(),
            "final_experience": result.calculate_final_experience(),
            "is_overdue": result.is_overdue(),
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "quest_creation_response.json")

    def test_quest_completion_response_snapshot(self, snapshot):
        """Test quest completion API response structure"""
        # Mock active quest
        mock_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python Programming"),
            description=QuestDescription("Complete comprehensive Python tutorial"),
            difficulty=QuestDifficulty.HARD,
            quest_type=QuestType.MAIN,
            status=QuestStatus.ACTIVE,
            experience_reward=ExperienceReward(200),
            start_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 15, 14, 30, 0),
        )

        # Mock completed quest
        completed_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python Programming"),
            description=QuestDescription("Complete comprehensive Python tutorial"),
            difficulty=QuestDifficulty.HARD,
            quest_type=QuestType.MAIN,
            status=QuestStatus.COMPLETED,
            experience_reward=ExperienceReward(200),
            start_date=date(2024, 1, 1),
            due_date=date(2024, 1, 31),
            completed_at=datetime(2024, 1, 15, 14, 30, 0),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 15, 14, 30, 0),
        )

        self.mock_repository.get_by_id.return_value = mock_quest
        self.mock_repository.save.return_value = completed_quest

        # Complete quest
        result_quest, experience_gained = self.quest_service.complete_quest(QuestId(1))

        # Convert to API response format
        api_response = {
            "quest": {
                "quest_id": result_quest.quest_id.value,
                "user_id": result_quest.user_id.value,
                "title": result_quest.title.value,
                "description": result_quest.description.value,
                "difficulty": result_quest.difficulty.value,
                "quest_type": result_quest.quest_type.value,
                "status": result_quest.status.value,
                "experience_reward": result_quest.experience_reward.value,
                "start_date": result_quest.start_date.isoformat()
                if result_quest.start_date
                else None,
                "due_date": result_quest.due_date.isoformat()
                if result_quest.due_date
                else None,
                "completed_at": result_quest.completed_at.isoformat()
                if result_quest.completed_at
                else None,
                "created_at": result_quest.created_at.isoformat(),
                "updated_at": result_quest.updated_at.isoformat(),
            },
            "experience_gained": experience_gained,
            "difficulty_multiplier": result_quest.get_difficulty_multiplier(),
            "completion_timestamp": result_quest.completed_at.isoformat()
            if result_quest.completed_at
            else None,
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "quest_completion_response.json")

    def test_quest_list_response_snapshot(self, snapshot):
        """Test quest list API response structure"""
        # Mock multiple quests
        mock_quests = [
            Quest(
                quest_id=QuestId(1),
                user_id=UserId(1),
                title=QuestTitle("Learn Python"),
                description=QuestDescription("Python tutorial"),
                difficulty=QuestDifficulty.MEDIUM,
                quest_type=QuestType.MAIN,
                status=QuestStatus.ACTIVE,
                experience_reward=ExperienceReward(150),
                created_at=datetime(2024, 1, 1, 10, 0, 0),
                updated_at=datetime(2024, 1, 1, 10, 0, 0),
            ),
            Quest(
                quest_id=QuestId(2),
                user_id=UserId(1),
                title=QuestTitle("Daily Exercise"),
                description=QuestDescription("30 minutes workout"),
                difficulty=QuestDifficulty.EASY,
                quest_type=QuestType.DAILY,
                status=QuestStatus.COMPLETED,
                experience_reward=ExperienceReward(25),
                completed_at=datetime(2024, 1, 15, 8, 0, 0),
                created_at=datetime(2024, 1, 15, 7, 0, 0),
                updated_at=datetime(2024, 1, 15, 8, 0, 0),
            ),
        ]

        self.mock_repository.get_user_quests.return_value = mock_quests

        # Convert to API response format
        api_response = {
            "quests": [
                {
                    "quest_id": quest.quest_id.value,
                    "user_id": quest.user_id.value,
                    "title": quest.title.value,
                    "description": quest.description.value,
                    "difficulty": quest.difficulty.value,
                    "quest_type": quest.quest_type.value,
                    "status": quest.status.value,
                    "experience_reward": quest.experience_reward.value,
                    "start_date": quest.start_date.isoformat()
                    if quest.start_date
                    else None,
                    "due_date": quest.due_date.isoformat() if quest.due_date else None,
                    "completed_at": quest.completed_at.isoformat()
                    if quest.completed_at
                    else None,
                    "created_at": quest.created_at.isoformat(),
                    "updated_at": quest.updated_at.isoformat(),
                    "difficulty_multiplier": quest.get_difficulty_multiplier(),
                    "final_experience": quest.calculate_final_experience(),
                    "is_overdue": quest.is_overdue(),
                }
                for quest in mock_quests
            ],
            "total_count": len(mock_quests),
            "active_count": len(
                [q for q in mock_quests if q.status == QuestStatus.ACTIVE]
            ),
            "completed_count": len(
                [q for q in mock_quests if q.status == QuestStatus.COMPLETED]
            ),
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "quest_list_response.json")


class TestHabitAPISnapshots:
    """Snapshot tests for Habit API responses"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_habit_repository = Mock()
        self.mock_completion_repository = Mock()
        self.habit_service = HabitService(
            self.mock_habit_repository, self.mock_completion_repository
        )

    def test_habit_creation_response_snapshot(self, snapshot):
        """Test habit creation API response structure"""
        # Mock repository response
        mock_habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Daily Exercise"),
            description="30 minutes of physical activity",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(0),
            longest_streak=StreakCount(0),
            experience_reward=ExperienceReward(25),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        self.mock_habit_repository.save.return_value = mock_habit

        # Create habit through service
        result = self.habit_service.create_habit(
            user_id=UserId(1),
            name="Daily Exercise",
            description="30 minutes of physical activity",
            frequency="daily",
            target_count=1,
            experience_reward=25,
        )

        # Convert to API response format
        api_response = {
            "habit_id": result.habit_id.value,
            "user_id": result.user_id.value,
            "name": result.name.value,
            "description": result.description,
            "frequency": result.frequency.value,
            "target_count": result.target_count.value,
            "current_streak": result.current_streak.value,
            "longest_streak": result.longest_streak.value,
            "experience_reward": result.experience_reward.value,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat(),
            "streak_bonus": result.calculate_streak_bonus(),
            "current_milestone": result.get_streak_milestone_type(),
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "habit_creation_response.json")

    def test_habit_completion_response_snapshot(self, snapshot):
        """Test habit completion API response structure"""
        # Mock habit with existing streak
        mock_habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Daily Exercise"),
            description="30 minutes of physical activity",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(7),
            longest_streak=StreakCount(15),
            experience_reward=ExperienceReward(25),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 8, 8, 0, 0),
        )

        # Mock completion
        mock_completion = HabitCompletion(
            completion_id="550e8400-e29b-41d4-a716-446655440000",
            habit_id=HabitId(1),
            count=CompletionCount(1),
            completion_date=date(2024, 1, 8),
            notes="Great morning workout!",
            experience_gained=ExperienceReward(30),
            created_at=datetime(2024, 1, 8, 8, 30, 0),
        )

        self.mock_habit_repository.get_by_id.return_value = mock_habit
        self.mock_completion_repository.get_latest_completion.return_value = None
        self.mock_completion_repository.save.return_value = mock_completion

        # Complete habit
        result_completion, experience_gained = self.habit_service.complete_habit(
            habit_id=HabitId(1),
            completion_count=1,
            completion_date=date(2024, 1, 8),
            notes="Great morning workout!",
        )

        # Convert to API response format
        api_response = {
            "completion": {
                "completion_id": result_completion.completion_id,
                "habit_id": result_completion.habit_id.value,
                "count": result_completion.count.value,
                "completion_date": result_completion.completion_date.isoformat(),
                "notes": result_completion.notes,
                "experience_gained": result_completion.experience_gained.value,
                "created_at": result_completion.created_at.isoformat(),
            },
            "experience_gained": experience_gained,
            "streak_info": {
                "current_streak": mock_habit.current_streak.value,
                "longest_streak": mock_habit.longest_streak.value,
                "streak_bonus": mock_habit.calculate_streak_bonus(),
                "milestone_reached": mock_habit.get_streak_milestone_type(),
            },
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "habit_completion_response.json")

    def test_habit_analytics_response_snapshot(self, snapshot):
        """Test habit analytics API response structure"""
        # Mock habit with analytics data
        mock_habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Daily Exercise"),
            description="30 minutes of physical activity",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(21),
            longest_streak=StreakCount(45),
            experience_reward=ExperienceReward(25),
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 22, 8, 0, 0),
        )

        self.mock_habit_repository.get_by_id.return_value = mock_habit

        # Mock completions for consistency calculation
        mock_completions = [
            HabitCompletion(
                completion_id=f"completion-{i}",
                habit_id=HabitId(1),
                count=CompletionCount(1),
                completion_date=date(2024, 1, i),
                notes="",
                experience_gained=ExperienceReward(25),
            )
            for i in range(1, 22)  # 21 completions
        ]
        self.mock_completion_repository.get_habit_completions.return_value = (
            mock_completions
        )

        # Calculate analytics
        consistency = self.habit_service.calculate_habit_consistency(
            HabitId(1), days=30
        )
        milestones = self.habit_service.get_streak_milestones(HabitId(1))

        # Convert to API response format
        api_response = {
            "habit_id": mock_habit.habit_id.value,
            "analytics": {
                "consistency_rate": consistency,
                "current_streak": mock_habit.current_streak.value,
                "longest_streak": mock_habit.longest_streak.value,
                "streak_bonus_multiplier": mock_habit.calculate_streak_bonus(),
                "achieved_milestones": milestones,
                "total_completions": len(mock_completions),
                "completion_rate_30_days": consistency,
            },
            "streak_info": {
                "current_milestone": mock_habit.get_streak_milestone_type(),
                "next_milestone": "month"
                if mock_habit.current_streak.value < 30
                else "dedication",
                "days_to_next_milestone": max(0, 30 - mock_habit.current_streak.value),
            },
        }

        # Snapshot the response structure
        assert_json_snapshot(snapshot, api_response, "habit_analytics_response.json")
