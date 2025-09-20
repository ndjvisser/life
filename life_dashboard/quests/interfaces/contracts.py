"""
Quests API contracts - Pydantic models for request/response validation.
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class QuestCreateRequest(BaseModel):
    """Request model for creating a quest."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)
    quest_type: str = Field(
        "main", regex="^(life_goal|annual_goal|main|side|weekly|daily)$"
    )
    difficulty: str = Field("medium", regex="^(easy|medium|hard|legendary)$")
    experience_reward: int = Field(10, ge=1, le=10000)
    start_date: Optional[date] = None
    due_date: Optional[date] = None

    @validator("due_date")
    def validate_due_date(cls, v, values):
        if (
            v
            and "start_date" in values
            and values["start_date"]
            and v < values["start_date"]
        ):
            raise ValueError("Due date cannot be before start date")
        return v


class QuestUpdateRequest(BaseModel):
    """Request model for updating a quest."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    quest_type: Optional[str] = Field(
        None, regex="^(life_goal|annual_goal|main|side|weekly|daily)$"
    )
    difficulty: Optional[str] = Field(None, regex="^(easy|medium|hard|legendary)$")
    experience_reward: Optional[int] = Field(None, ge=1, le=10000)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)


class QuestResponse(BaseModel):
    """Response model for quest data."""

    quest_id: str
    title: str
    description: str
    quest_type: str
    difficulty: str
    status: str
    experience_reward: int
    completion_percentage: float
    start_date: Optional[date]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    is_overdue: bool
    days_until_due: Optional[int]
    final_experience_reward: int
    created_at: datetime
    updated_at: datetime


class QuestListResponse(BaseModel):
    """Response model for quest lists."""

    quests: List[QuestResponse]
    total_count: int
    active_count: int
    completed_count: int
    overdue_count: int


class QuestActionRequest(BaseModel):
    """Request model for quest actions."""

    action: str = Field(..., regex="^(start|complete|pause|resume|fail)$")
    reason: Optional[str] = Field(None, max_length=500)
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)


class QuestActionResponse(BaseModel):
    """Response model for quest actions."""

    quest: QuestResponse
    experience_awarded: Optional[int] = None
    level_up_occurred: bool = False
    message: str
    success: bool = True


class HabitCreateRequest(BaseModel):
    """Request model for creating a habit."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    frequency: str = Field("daily", regex="^(daily|weekly|monthly|custom)$")
    target_count: int = Field(1, ge=1, le=100)
    experience_reward: int = Field(5, ge=1, le=1000)


class HabitUpdateRequest(BaseModel):
    """Request model for updating a habit."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|custom)$")
    target_count: Optional[int] = Field(None, ge=1, le=100)
    experience_reward: Optional[int] = Field(None, ge=1, le=1000)


class HabitResponse(BaseModel):
    """Response model for habit data."""

    habit_id: str
    name: str
    description: str
    frequency: str
    target_count: int
    current_streak: int
    longest_streak: int
    experience_reward: int
    last_completed: Optional[date]
    is_due_today: bool
    completion_rate_30d: float
    created_at: datetime
    updated_at: datetime


class HabitListResponse(BaseModel):
    """Response model for habit lists."""

    habits: List[HabitResponse]
    total_count: int
    due_today_count: int
    active_streaks_count: int
    longest_streak: int


class HabitCompletionRequest(BaseModel):
    """Request model for completing a habit."""

    completion_date: Optional[date] = None
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
    created_at: datetime


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
    status: Optional[str] = Field(
        None, regex="^(draft|active|completed|failed|paused)$"
    )
    quest_type: Optional[str] = Field(
        None, regex="^(life_goal|annual_goal|main|side|weekly|daily)$"
    )
    limit: int = Field(20, ge=1, le=100)


class HabitSearchRequest(BaseModel):
    """Request model for searching habits."""

    query: str = Field(..., min_length=1, max_length=100)
    frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly|custom)$")
    limit: int = Field(20, ge=1, le=100)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None
