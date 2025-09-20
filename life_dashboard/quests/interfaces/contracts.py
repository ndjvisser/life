"""
Quests API contracts - Pydantic models for request/response validation.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from life_dashboard.quests.domain.entities import (
    HabitFrequency,
    QuestDifficulty,
    QuestStatus,
    QuestType,
)


class QuestCreateRequest(BaseModel):
    """Request model for creating a quest."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)
    quest_type: QuestType = QuestType.MAIN
    difficulty: QuestDifficulty = QuestDifficulty.MEDIUM
    experience_reward: int = Field(10, ge=1, le=10000)
    start_date: date | None = None
    due_date: date | None = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(
        cls, v: date | None, info: ValidationInfo
    ) -> date | None:
        """
        Validator to ensure a provided due date is not earlier than the start date.

        Checks that when both `start_date` (read from the already-validated `info.data`)
        and the candidate `v` (due date) are present and non-null, `v` is greater than or
        equal to `start_date`.

        Parameters:
            cls: The validator's owner class (unused).
            v: The candidate due date value to validate.
            info: Pydantic validation context containing previously-validated values.

        Returns:
            The validated due date (`v`) unchanged.

        Raises:
            ValueError: If `v` is before `start_date`.
        """
        start_date = info.data.get("start_date") if info.data else None

        if v and start_date and v < start_date:
            raise ValueError("Due date cannot be before start date")
        return v


class QuestUpdateRequest(BaseModel):
    """Request model for updating a quest."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    quest_type: QuestType | None = None
    difficulty: QuestDifficulty | None = None
    experience_reward: int | None = Field(None, ge=1, le=10000)
    start_date: date | None = None
    due_date: date | None = None
    completion_percentage: float | None = Field(None, ge=0, le=100)


class QuestResponse(BaseModel):
    """Response model for quest data."""

    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    difficulty: QuestDifficulty
    status: QuestStatus
    experience_reward: int
    completion_percentage: float
    start_date: date | None
    due_date: date | None
    completed_at: datetime | None
    is_overdue: bool
    days_until_due: int | None
    final_experience_reward: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class QuestListResponse(BaseModel):
    """Response model for quest lists."""

    quests: list[QuestResponse]
    total_count: int
    active_count: int
    completed_count: int
    overdue_count: int


class QuestActionRequest(BaseModel):
    """Request model for quest actions."""

    action: str = Field(..., regex="^(start|complete|pause|resume|fail)$")
    reason: str | None = Field(None, max_length=500)
    completion_percentage: float | None = Field(None, ge=0, le=100)


class QuestActionResponse(BaseModel):
    """Response model for quest actions."""

    quest: QuestResponse
    experience_awarded: int | None = None
    level_up_occurred: bool = False
    message: str
    success: bool = True


class HabitCreateRequest(BaseModel):
    """Request model for creating a habit."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_count: int = Field(1, ge=1, le=100)
    experience_reward: int = Field(5, ge=1, le=1000)


class HabitUpdateRequest(BaseModel):
    """Request model for updating a habit."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    frequency: HabitFrequency | None = None
    target_count: int | None = Field(None, ge=1, le=100)
    experience_reward: int | None = Field(None, ge=1, le=1000)


class HabitResponse(BaseModel):
    """Response model for habit data."""

    habit_id: str
    name: str
    description: str
    frequency: HabitFrequency
    target_count: int
    current_streak: int
    longest_streak: int
    experience_reward: int
    last_completed: date | None
    is_due_today: bool
    completion_rate_30d: float
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HabitListResponse(BaseModel):
    """Response model for habit lists."""

    habits: list[HabitResponse]
    total_count: int
    due_today_count: int
    active_streaks_count: int
    longest_streak: int


class HabitCompletionRequest(BaseModel):
    """Request model for completing a habit."""

    completion_date: date | None = None
    count: int = Field(1, ge=1, le=100)
    notes: str = Field("", max_length=500)


class HabitCompletionResponse(BaseModel):
    """Response model for habit completion."""

    completion_id: str
    habit_id: str
    completion_date: date
    count: int
    notes: str
    experience_gained: int
    streak_at_completion: int
    created_at: datetime | None = None


class HabitCompletionActionResponse(BaseModel):
    """Response model for habit completion action."""

    habit: HabitResponse
    completion: HabitCompletionResponse
    experience_awarded: int
    streak_milestone_reached: bool = False
    message: str
    success: bool = True


class QuestStatisticsResponse(BaseModel):
    """Response model for quest statistics."""

    total_quests: int
    active_quests: int
    completed_quests: int
    failed_quests: int
    overdue_quests: int
    completion_rate: float
    total_experience_earned: int
    average_completion_time: float


class HabitStatisticsResponse(BaseModel):
    """Response model for habit statistics."""

    total_habits: int
    active_streaks: int
    longest_streak: int
    total_completions: int
    completion_rate: float
    total_experience_earned: int
    streak_milestones: int
    habits_due_today: int


class QuestSearchRequest(BaseModel):
    """Request model for searching quests."""

    query: str = Field(..., min_length=1, max_length=100)
    status: QuestStatus | None = None
    quest_type: QuestType | None = None
    limit: int = Field(20, ge=1, le=100)


class HabitSearchRequest(BaseModel):
    """Request model for searching habits."""

    query: str = Field(..., min_length=1, max_length=100)
    frequency: HabitFrequency | None = None
    limit: int = Field(20, ge=1, le=100)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    message: str
    error_code: str | None = None
    details: dict | None = None
