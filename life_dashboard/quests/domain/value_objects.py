"""
Quests domain value objects - immutable objects that represent concepts.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional


class QuestPriority(Enum):
    """Quest priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StreakType(Enum):
    """Types of streaks for habits."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass(frozen=True)
class QuestReward:
    """Value object for quest rewards."""

    experience_points: int
    bonus_multiplier: float = 1.0

    def __post_init__(self):
        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")
        if self.bonus_multiplier < 0:
            raise ValueError("Bonus multiplier cannot be negative")

    def calculate_total_experience(self) -> int:
        """Calculate total experience with bonus."""
        return int(self.experience_points * self.bonus_multiplier)

    def with_bonus(self, multiplier: float) -> "QuestReward":
        """Create new reward with additional bonus multiplier."""
        return QuestReward(
            experience_points=self.experience_points,
            bonus_multiplier=self.bonus_multiplier * multiplier,
        )


@dataclass(frozen=True)
class QuestDeadline:
    """Value object for quest deadlines."""

    due_date: date
    buffer_days: int = 0

    def __post_init__(self):
        if self.buffer_days < 0:
            raise ValueError("Buffer days cannot be negative")

    @property
    def effective_deadline(self) -> date:
        """Get the effective deadline including buffer."""
        return self.due_date - timedelta(days=self.buffer_days)

    def is_overdue(self, current_date: Optional[date] = None) -> bool:
        """Check if deadline has passed."""
        if current_date is None:
            current_date = date.today()
        return current_date > self.due_date

    def is_approaching(
        self, warning_days: int = 3, current_date: Optional[date] = None
    ) -> bool:
        """Check if deadline is approaching within warning period."""
        if current_date is None:
            current_date = date.today()

        warning_date = self.effective_deadline - timedelta(days=warning_days)
        return current_date >= warning_date and not self.is_overdue(current_date)

    def days_remaining(self, current_date: Optional[date] = None) -> int:
        """Calculate days remaining until deadline."""
        if current_date is None:
            current_date = date.today()

        delta = self.due_date - current_date
        return delta.days


@dataclass(frozen=True)
class HabitStreak:
    """Value object for habit streaks."""

    current_count: int
    longest_count: int
    streak_type: StreakType
    last_completion_date: Optional[date] = None

    def __post_init__(self):
        if self.current_count < 0:
            raise ValueError("Current streak count cannot be negative")
        if self.longest_count < 0:
            raise ValueError("Longest streak count cannot be negative")
        if self.current_count > self.longest_count:
            raise ValueError("Current streak cannot be longer than longest streak")

    def is_active(self, current_date: Optional[date] = None) -> bool:
        """Check if streak is still active."""
        if self.current_count == 0 or not self.last_completion_date:
            return False

        if current_date is None:
            current_date = date.today()

        days_since_last = (current_date - self.last_completion_date).days

        # Streak is broken if too many days have passed
        if self.streak_type == StreakType.DAILY:
            return days_since_last <= 1
        elif self.streak_type == StreakType.WEEKLY:
            return days_since_last <= 7
        elif self.streak_type == StreakType.MONTHLY:
            return days_since_last <= 31

        return False

    def extend_streak(self, completion_date: date) -> "HabitStreak":
        """Create new streak with extended count."""
        if not self.is_active(completion_date):
            # Streak was broken, start new one
            return HabitStreak(
                current_count=1,
                longest_count=max(1, self.longest_count),
                streak_type=self.streak_type,
                last_completion_date=completion_date,
            )

        new_current = self.current_count + 1
        new_longest = max(new_current, self.longest_count)

        return HabitStreak(
            current_count=new_current,
            longest_count=new_longest,
            streak_type=self.streak_type,
            last_completion_date=completion_date,
        )

    def break_streak(self) -> "HabitStreak":
        """Create new streak with broken current count."""
        return HabitStreak(
            current_count=0,
            longest_count=self.longest_count,
            streak_type=self.streak_type,
            last_completion_date=self.last_completion_date,
        )

    def get_milestone_level(self) -> Optional[str]:
        """Get milestone level for current streak."""
        if self.current_count >= 365:
            return "legendary"
        elif self.current_count >= 180:
            return "master"
        elif self.current_count >= 90:
            return "expert"
        elif self.current_count >= 30:
            return "advanced"
        elif self.current_count >= 14:
            return "intermediate"
        elif self.current_count >= 7:
            return "beginner"

        return None


@dataclass(frozen=True)
class QuestProgress:
    """Value object for quest progress tracking."""

    completion_percentage: float
    milestones_completed: List[str]

    def __post_init__(self):
        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

    def is_complete(self) -> bool:
        """Check if quest is complete."""
        return self.completion_percentage >= 100.0

    def update_progress(self, new_percentage: float) -> "QuestProgress":
        """Create new progress with updated percentage."""
        if not 0 <= new_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        return QuestProgress(
            completion_percentage=new_percentage,
            milestones_completed=self.milestones_completed,
        )

    def add_milestone(self, milestone: str) -> "QuestProgress":
        """Create new progress with added milestone."""
        if milestone in self.milestones_completed:
            return self  # Milestone already exists

        new_milestones = self.milestones_completed + [milestone]
        return QuestProgress(
            completion_percentage=self.completion_percentage,
            milestones_completed=new_milestones,
        )

    def get_progress_level(self) -> str:
        """Get descriptive progress level."""
        if self.completion_percentage >= 100:
            return "complete"
        elif self.completion_percentage >= 75:
            return "nearly_complete"
        elif self.completion_percentage >= 50:
            return "halfway"
        elif self.completion_percentage >= 25:
            return "started"
        else:
            return "not_started"


@dataclass(frozen=True)
class HabitSchedule:
    """Value object for habit scheduling."""

    frequency_days: int
    target_count_per_period: int
    flexible_scheduling: bool = False

    def __post_init__(self):
        if self.frequency_days <= 0:
            raise ValueError("Frequency days must be positive")
        if self.target_count_per_period <= 0:
            raise ValueError("Target count must be positive")

    def is_due(
        self, last_completion: Optional[date], current_date: Optional[date] = None
    ) -> bool:
        """Check if habit is due based on schedule."""
        if current_date is None:
            current_date = date.today()

        if not last_completion:
            return True

        days_since_last = (current_date - last_completion).days

        if self.flexible_scheduling:
            # Allow some flexibility in scheduling
            return days_since_last >= (self.frequency_days - 1)
        else:
            # Strict scheduling
            return days_since_last >= self.frequency_days

    def next_due_date(self, last_completion: Optional[date]) -> date:
        """Calculate next due date."""
        if not last_completion:
            return date.today()

        return last_completion + timedelta(days=self.frequency_days)

    def completion_window_days(self) -> int:
        """Get the window of days for completing this habit."""
        if self.flexible_scheduling:
            return max(1, self.frequency_days // 2)
        else:
            return 1
