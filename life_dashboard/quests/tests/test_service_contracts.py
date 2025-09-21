"""
Contract tests for Quest domain services using Pydantic models.

These tests validate service layer APIs and ensure consistent interfaces.
"""

from datetime import date, datetime, timezone
from unittest.mock import Mock

import pytest

pytest.importorskip("pydantic")
from pydantic import BaseModel, ValidationError

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


# Pydantic models for API contracts
class QuestCreateRequest(BaseModel):
    """Contract for quest creation requests"""

    user_id: int
    title: str
    description: str
    difficulty: str
    quest_type: str
    experience_reward: int
    start_date: date | None = None
    due_date: date | None = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Learn Python",
                "description": "Complete Python tutorial",
                "difficulty": "medium",
                "quest_type": "main",
                "experience_reward": 100,
                "start_date": "2024-01-01",
                "due_date": "2024-01-31",
            }
        }


class QuestResponse(BaseModel):
    """Contract for quest responses"""

    quest_id: int
    user_id: int
    title: str
    description: str
    difficulty: str
    quest_type: str
    status: str
    experience_reward: int
    start_date: date | None
    due_date: date | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "quest_id": 1,
                "user_id": 1,
                "title": "Learn Python",
                "description": "Complete Python tutorial",
                "difficulty": "medium",
                "quest_type": "main",
                "status": "active",
                "experience_reward": 100,
                "start_date": "2024-01-01",
                "due_date": "2024-01-31",
                "completed_at": None,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
            }
        }


class QuestCompletionResponse(BaseModel):
    """Contract for quest completion responses"""

    quest: QuestResponse
    experience_gained: int

    class Config:
        schema_extra = {
            "example": {
                "quest": {
                    "quest_id": 1,
                    "status": "completed",
                    "completed_at": "2024-01-15T14:30:00",
                },
                "experience_gained": 150,
            }
        }


class HabitCreateRequest(BaseModel):
    """Contract for habit creation requests"""

    user_id: int
    name: str
    description: str
    frequency: str
    target_count: int
    experience_reward: int

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "name": "Exercise",
                "description": "Daily workout routine",
                "frequency": "daily",
                "target_count": 1,
                "experience_reward": 25,
            }
        }


class HabitResponse(BaseModel):
    """Contract for habit responses"""

    habit_id: int
    user_id: int
    name: str
    description: str
    frequency: str
    target_count: int
    current_streak: int
    longest_streak: int
    experience_reward: int
    created_at: datetime
    updated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "habit_id": 1,
                "user_id": 1,
                "name": "Exercise",
                "description": "Daily workout routine",
                "frequency": "daily",
                "target_count": 1,
                "current_streak": 5,
                "longest_streak": 10,
                "experience_reward": 25,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
            }
        }


class HabitCompletionRequest(BaseModel):
    """Contract for habit completion requests"""

    habit_id: int
    completion_count: int = 1
    completion_date: date | None = None
    notes: str = ""

    class Config:
        schema_extra = {
            "example": {
                "habit_id": 1,
                "completion_count": 1,
                "completion_date": "2024-01-15",
                "notes": "Great workout today!",
            }
        }


class HabitCompletionResponse(BaseModel):
    """Contract for habit completion responses"""

    completion_id: str
    habit_id: int
    count: int
    completion_date: date
    notes: str
    experience_gained: int
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "completion_id": "uuid-string",
                "habit_id": 1,
                "count": 1,
                "completion_date": "2024-01-15",
                "notes": "Great workout today!",
                "experience_gained": 30,
                "created_at": "2024-01-15T14:30:00",
            }
        }


class TestQuestServiceContracts:
    """Test QuestService API contracts"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_repository = Mock()
        self.quest_service = QuestService(self.mock_repository)

    def test_create_quest_contract_validation(self):
        """Test quest creation request contract validation"""
        # Valid request should pass validation
        valid_request = QuestCreateRequest(
            user_id=1,
            title="Learn Python",
            description="Complete Python tutorial",
            difficulty="medium",
            quest_type="main",
            experience_reward=100,
        )

        assert valid_request.user_id == 1
        assert valid_request.title == "Learn Python"
        assert valid_request.difficulty == "medium"

    def test_create_quest_contract_validation_errors(self):
        """Test quest creation request validation errors"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            QuestCreateRequest(
                user_id=1,
                # Missing title
                description="Test",
                difficulty="medium",
                quest_type="main",
                experience_reward=100,
            )

        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            QuestCreateRequest(
                user_id="invalid",  # Should be int
                title="Test",
                description="Test",
                difficulty="medium",
                quest_type="main",
                experience_reward=100,
            )

    def test_quest_service_create_returns_valid_response(self):
        """Test that quest service returns valid response contract"""
        # Mock repository to return a quest
        mock_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python"),
            description=QuestDescription("Complete Python tutorial"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.DRAFT,
            experience_reward=ExperienceReward(100),
        )
        self.mock_repository.save.return_value = mock_quest

        # Create quest through service
        result = self.quest_service.create_quest(
            user_id=UserId(1),
            title="Learn Python",
            description="Complete Python tutorial",
            difficulty="medium",
            quest_type="main",
            experience_reward=100,
        )

        # Validate response can be serialized to contract
        response_data = {
            "quest_id": result.quest_id.value,
            "user_id": result.user_id.value,
            "title": result.title.value,
            "description": result.description.value,
            "difficulty": result.difficulty.value,
            "quest_type": result.quest_type.value,
            "status": result.status.value,
            "experience_reward": result.experience_reward.value,
            "start_date": result.start_date,
            "due_date": result.due_date,
            "completed_at": result.completed_at,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }

        # Should not raise validation error
        response = QuestResponse(**response_data)
        assert response.quest_id == 1
        assert response.title == "Learn Python"

    def test_complete_quest_returns_valid_completion_response(self):
        """Test that quest completion returns valid response contract"""
        # Mock quest
        mock_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python"),
            description=QuestDescription("Complete Python tutorial"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.ACTIVE,
            experience_reward=ExperienceReward(100),
        )

        # Mock completed quest
        completed_quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python"),
            description=QuestDescription("Complete Python tutorial"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.COMPLETED,
            experience_reward=ExperienceReward(100),
            completed_at=datetime.now(timezone.utc),
        )

        self.mock_repository.get_by_id.return_value = mock_quest
        self.mock_repository.save.return_value = completed_quest

        # Complete quest
        result_quest, experience_gained = self.quest_service.complete_quest(QuestId(1))

        # Validate completion response contract
        quest_data = {
            "quest_id": result_quest.quest_id.value,
            "user_id": result_quest.user_id.value,
            "title": result_quest.title.value,
            "description": result_quest.description.value,
            "difficulty": result_quest.difficulty.value,
            "quest_type": result_quest.quest_type.value,
            "status": result_quest.status.value,
            "experience_reward": result_quest.experience_reward.value,
            "start_date": result_quest.start_date,
            "due_date": result_quest.due_date,
            "completed_at": result_quest.completed_at,
            "created_at": result_quest.created_at,
            "updated_at": result_quest.updated_at,
        }

        completion_response = QuestCompletionResponse(
            quest=QuestResponse(**quest_data), experience_gained=experience_gained
        )

        assert completion_response.experience_gained > 0
        assert completion_response.quest.status == "completed"


class TestHabitServiceContracts:
    """Test HabitService API contracts"""

    def setup_method(self):
        """Set up test dependencies"""
        self.mock_habit_repository = Mock()
        self.mock_completion_repository = Mock()
        self.habit_service = HabitService(
            self.mock_habit_repository, self.mock_completion_repository
        )

    def test_create_habit_contract_validation(self):
        """Test habit creation request contract validation"""
        # Valid request should pass validation
        valid_request = HabitCreateRequest(
            user_id=1,
            name="Exercise",
            description="Daily workout routine",
            frequency="daily",
            target_count=1,
            experience_reward=25,
        )

        assert valid_request.user_id == 1
        assert valid_request.name == "Exercise"
        assert valid_request.frequency == "daily"

    def test_habit_completion_contract_validation(self):
        """Test habit completion request contract validation"""
        # Valid request should pass validation
        valid_request = HabitCompletionRequest(
            habit_id=1,
            completion_count=2,
            completion_date=date.today(),
            notes="Great workout!",
        )

        assert valid_request.habit_id == 1
        assert valid_request.completion_count == 2

        # Default values should work
        minimal_request = HabitCompletionRequest(habit_id=1)
        assert minimal_request.completion_count == 1
        assert minimal_request.notes == ""

    def test_habit_service_create_returns_valid_response(self):
        """Test that habit service returns valid response contract"""
        # Mock repository to return a habit
        mock_habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout routine",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(0),
            longest_streak=StreakCount(0),
            experience_reward=ExperienceReward(25),
        )
        self.mock_habit_repository.create.return_value = mock_habit

        # Create habit through service
        result = self.habit_service.create_habit(
            user_id=UserId(1),
            name="Exercise",
            description="Daily workout routine",
            frequency="daily",
            target_count=1,
            experience_reward=25,
        )

        # Validate response can be serialized to contract
        response_data = {
            "habit_id": result.habit_id.value,
            "user_id": result.user_id.value,
            "name": result.name.value,
            "description": result.description,
            "frequency": result.frequency.value,
            "target_count": result.target_count.value,
            "current_streak": result.current_streak.value,
            "longest_streak": result.longest_streak.value,
            "experience_reward": result.experience_reward.value,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }

        # Should not raise validation error
        response = HabitResponse(**response_data)
        assert response.habit_id == 1
        assert response.name == "Exercise"

    def test_habit_service_create_raises_for_invalid_repository_response(self):
        """Habit creation should surface repository contract violations."""

        self.mock_habit_repository.create.return_value = object()

        with pytest.raises(TypeError) as exc_info:
            self.habit_service.create_habit(
                user_id=UserId(1),
                name="Exercise",
                description="Daily workout routine",
                frequency="daily",
                target_count=1,
                experience_reward=25,
            )

        assert "HabitRepository must return Habit instances" in str(exc_info.value)
        self.mock_habit_repository.save.assert_not_called()

    def test_complete_habit_returns_valid_completion_response(self):
        """Test that habit completion returns valid response contract"""
        # Mock habit
        mock_habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout routine",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(5),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        # Mock completion
        mock_completion = HabitCompletion(
            completion_id="test-uuid",
            habit_id=HabitId(1),
            count=CompletionCount(1),
            completion_date=date.today(),
            notes="Great workout!",
            experience_gained=ExperienceReward(30),
        )

        self.mock_habit_repository.get_by_id.return_value = mock_habit
        self.mock_completion_repository.get_latest_completion.return_value = None
        self.mock_completion_repository.save.return_value = mock_completion

        # Complete habit
        result_completion, experience_gained = self.habit_service.complete_habit(
            habit_id=HabitId(1), completion_count=1, notes="Great workout!"
        )

        # Validate completion response contract
        completion_data = {
            "completion_id": result_completion.completion_id,
            "habit_id": result_completion.habit_id.value,
            "count": result_completion.count.value,
            "completion_date": result_completion.completion_date,
            "notes": result_completion.notes,
            "experience_gained": experience_gained,
            "created_at": result_completion.created_at,
        }

        completion_response = HabitCompletionResponse(**completion_data)
        assert completion_response.experience_gained > 0
        assert completion_response.habit_id == 1

    def test_contract_schema_examples_are_valid(self):
        """Test that all contract schema examples are valid"""
        # Test QuestCreateRequest example
        quest_example = QuestCreateRequest.Config.schema_extra["example"]
        quest_request = QuestCreateRequest(**quest_example)
        assert quest_request.title == "Learn Python"

        # Test HabitCreateRequest example
        habit_example = HabitCreateRequest.Config.schema_extra["example"]
        habit_request = HabitCreateRequest(**habit_example)
        assert habit_request.name == "Exercise"

        # Test HabitCompletionRequest example
        completion_example = HabitCompletionRequest.Config.schema_extra["example"]
        completion_request = HabitCompletionRequest(**completion_example)
        assert completion_request.notes == "Great workout today!"
