"""
Quest Domain Entities

Pure Python domain objects representing core quest business concepts.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from .value_objects import (
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


class QuestStatus(Enum):
    """Quest status enumeration"""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class QuestType(Enum):
    """Quest type enumeration"""

    LIFE_GOAL = "life_goal"
    ANNUAL_GOAL = "annual_goal"
    MAIN = "main"
    SIDE = "side"
    WEEKLY = "weekly"
    DAILY = "daily"


class QuestDifficulty(Enum):
    """Quest difficulty enumeration"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"


class HabitFrequency(Enum):
    """Habit frequency enumeration"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass(kw_only=True)
class Quest:
    """
    Quest domain entity representing a user's goal or task.

    Contains pure business logic for quest state transitions and validation.
    """

    user_id: UserId
    title: QuestTitle
    description: QuestDescription
    difficulty: QuestDifficulty
    quest_type: QuestType
    status: QuestStatus
    experience_reward: ExperienceReward
    quest_id: Optional[QuestId] = None
    parent_quest_id: str | None = None
    prerequisite_quest_ids: list[str] = field(default_factory=list)
    progress: float = 0.0
    start_date: date | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate quest data after initialization"""
        if self.parent_quest_id is not None:
            self.parent_quest_id = str(self.parent_quest_id)

        if self.prerequisite_quest_ids is None:
            self.prerequisite_quest_ids = []
        elif not isinstance(self.prerequisite_quest_ids, list):
            self.prerequisite_quest_ids = [
                str(prereq) for prereq in self.prerequisite_quest_ids
            ]
        else:
            self.prerequisite_quest_ids = [
                str(prereq) for prereq in self.prerequisite_quest_ids
            ]

        self._validate_dates()
        self._validate_status_transitions()
        self._validate_progress()

    def _validate_dates(self):
        """Validate date constraints"""
        if self.start_date and self.due_date:
            if self.start_date > self.due_date:
                raise ValueError("Start date cannot be after due date")

        if self.completed_at and self.status != QuestStatus.COMPLETED:
            raise ValueError("Completed timestamp only valid for completed quests")

    def _validate_status_transitions(self):
        """Validate status is appropriate for quest type"""
        if self.quest_type in [QuestType.DAILY, QuestType.WEEKLY]:
            if self.status == QuestStatus.PAUSED:
                raise ValueError("Daily/Weekly quests cannot be paused")

    def _validate_progress(self):
        """Validate that quest progress is within the expected range"""
        if not 0.0 <= self.progress <= 100.0:
            raise ValueError("Quest progress must be between 0 and 100 percent")

    def can_transition_to(self, new_status: QuestStatus) -> bool:
        """Check if quest can transition to new status"""
        valid_transitions = {
            QuestStatus.DRAFT: [QuestStatus.ACTIVE, QuestStatus.FAILED],
            QuestStatus.ACTIVE: [
                QuestStatus.COMPLETED,
                QuestStatus.FAILED,
                QuestStatus.PAUSED,
            ],
            QuestStatus.PAUSED: [QuestStatus.ACTIVE, QuestStatus.FAILED],
            QuestStatus.COMPLETED: [],  # Terminal state
            QuestStatus.FAILED: [QuestStatus.ACTIVE],  # Can retry
        }

        return new_status in valid_transitions.get(self.status, [])

    def activate(self) -> None:
        """Activate the quest"""
        if not self.can_transition_to(QuestStatus.ACTIVE):
            raise ValueError(f"Cannot activate quest from {self.status.value} status")

        self.status = QuestStatus.ACTIVE
        if not self.start_date:
            self.start_date = date.today()
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Complete the quest"""
        if not self.can_transition_to(QuestStatus.COMPLETED):
            raise ValueError(f"Cannot complete quest from {self.status.value} status")

        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def fail(self) -> None:
        """Mark quest as failed"""
        if not self.can_transition_to(QuestStatus.FAILED):
            raise ValueError(f"Cannot fail quest from {self.status.value} status")

        self.status = QuestStatus.FAILED
        self.updated_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause the quest"""
        if self.quest_type in (QuestType.DAILY, QuestType.WEEKLY):
            raise ValueError("Daily and weekly quests cannot be paused")
        if not self.can_transition_to(QuestStatus.PAUSED):
            raise ValueError(f"Cannot pause quest from {self.status.value} status")

        self.status = QuestStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def get_difficulty_multiplier(self) -> float:
        """Get experience multiplier based on difficulty"""
        multipliers = {
            QuestDifficulty.EASY: 1.0,
            QuestDifficulty.MEDIUM: 1.5,
            QuestDifficulty.HARD: 2.0,
            QuestDifficulty.LEGENDARY: 3.0,
        }
        return multipliers[self.difficulty]

    def calculate_final_experience(self) -> int:
        """Calculate final experience reward with difficulty multiplier"""
        base_reward = self.experience_reward.value
        multiplier = self.get_difficulty_multiplier()
        return int(base_reward * multiplier)

    def is_overdue(self) -> bool:
        """Check if quest is overdue"""
        if not self.due_date or self.status in [
            QuestStatus.COMPLETED,
            QuestStatus.FAILED,
        ]:
            return False
        return date.today() > self.due_date


@dataclass(kw_only=True)
class Habit:
    """
    Habit domain entity representing a recurring user activity.

    Contains pure business logic for habit tracking and streak calculation.
    """

    user_id: UserId
    name: HabitName
    description: str
    frequency: HabitFrequency
    target_count: CompletionCount
    current_streak: StreakCount
    longest_streak: StreakCount
    experience_reward: ExperienceReward
    habit_id: Optional[HabitId] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate habit data after initialization"""
        if self.current_streak.value > self.longest_streak.value:
            raise ValueError("Current streak cannot exceed longest streak")

    def calculate_streak_bonus(self) -> float:
        """Calculate streak bonus multiplier"""
        streak = self.current_streak.value
        if streak < 7:
            return 1.0
        elif streak < 21:
            return 1.2
        elif streak < 50:
            return 1.5
        else:
            return 2.0

    def calculate_experience_reward(self, completion_count: int = 1) -> int:
        """Calculate experience reward for completion"""
        base_reward = self.experience_reward.value * completion_count
        streak_bonus = self.calculate_streak_bonus()
        return int(base_reward * streak_bonus)

    def complete_habit(
        self,
        completion_date: date,
        completion_count: int = 1,
        previous_completion_date: date | None = None,
    ) -> tuple[int, StreakCount, str | None]:
        """Apply completion logic and return experience, streak, and milestone information."""

        if completion_count <= 0:
            raise ValueError("Completion count must be positive")

        self.update_streak(completion_date, previous_completion_date)
        experience_gained = self.calculate_experience_reward(completion_count)
        milestone = self.get_streak_milestone_type()

        # Ensure timestamps reflect the completion action
        self.updated_at = datetime.utcnow()

        return experience_gained, self.current_streak, milestone

    def update_streak(
        self, completion_date: date, previous_completion_date: date | None = None
    ) -> None:
        """Update streak based on completion pattern"""
        if not previous_completion_date:
            # First completion or reset
            self.current_streak = StreakCount(1)
        else:
            days_diff = (completion_date - previous_completion_date).days
            # For monthly frequency, compute month-delta across years to handle Dec→Jan
            if self.frequency == HabitFrequency.MONTHLY:
                prev_idx = (
                    previous_completion_date.year * 12 + previous_completion_date.month
                )
                curr_idx = completion_date.year * 12 + completion_date.month
                month_delta = curr_idx - prev_idx
                is_consecutive = month_delta in (0, 1)
            else:
                is_consecutive = self._is_consecutive_completion(days_diff)

            if is_consecutive:
                new_streak = self.current_streak.value + 1
                self.current_streak = StreakCount(new_streak)

                # Update longest streak if needed
                if new_streak > self.longest_streak.value:
                    self.longest_streak = StreakCount(new_streak)
            else:
                # Streak broken, reset to 1
                self.current_streak = StreakCount(1)

        self.updated_at = datetime.utcnow()

    def _is_consecutive_completion(self, days_diff: int) -> bool:
        """Check if completion maintains streak based on frequency"""
        if self.frequency == HabitFrequency.DAILY:
            return days_diff == 1
        elif self.frequency == HabitFrequency.WEEKLY:
            return 6 <= days_diff <= 8  # Allow some flexibility
        elif self.frequency == HabitFrequency.MONTHLY:
            return 28 <= days_diff <= 32  # Allow some flexibility
        else:
            return True  # Custom frequency - assume consecutive

    def break_streak(self) -> None:
        """Break the current streak"""
        self.current_streak = StreakCount(0)
        self.updated_at = datetime.utcnow()

    def get_streak_milestone_type(self) -> str | None:
        """Get milestone type if current streak hits a milestone"""
        streak = self.current_streak.value
        milestones = {
            7: "week",
            21: "habit_formation",
            30: "month",
            50: "dedication",
            100: "mastery",
            365: "year",
        }
        return milestones.get(streak)


@dataclass
class HabitCompletion:
    """
    Habit completion domain entity representing a single habit completion.
    """

    completion_id: str
    habit_id: HabitId
    count: CompletionCount
    completion_date: date
    notes: str
    experience_gained: ExperienceReward
    user_id: UserId | None = None
    streak_at_completion: StreakCount | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Generate completion ID if not provided"""
        if not self.completion_id:
            self.completion_id = str(uuid4())
        # Ensure user_id is properly typed
        if self.user_id is not None and not isinstance(self.user_id, UserId):
            if isinstance(self.user_id, int):
                self.user_id = UserId(self.user_id)
            else:
                raise ValueError(f"Invalid user_id type: {type(self.user_id)}")
        # Ensure streak_at_completion is properly typed
        if self.streak_at_completion is None:
            self.streak_at_completion = StreakCount(0)
        elif not isinstance(self.streak_at_completion, StreakCount):
            if isinstance(self.streak_at_completion, int):
                self.streak_at_completion = StreakCount(self.streak_at_completion)
            else:
                raise ValueError(
                    f"Invalid streak_at_completion type: {type(self.streak_at_completion)}"
                )
