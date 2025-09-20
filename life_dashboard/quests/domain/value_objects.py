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
        """
        Validate QuestReward invariants after initialization.

        Ensures `experience_points` and `bonus_multiplier` are non-negative; raises ValueError if either is negative.
        """
        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")
        if self.bonus_multiplier < 0:
            raise ValueError("Bonus multiplier cannot be negative")

    def calculate_total_experience(self) -> int:
        """
        Return the total experience after applying the reward's bonus multiplier.

        The computed value is the product of `experience_points` and `bonus_multiplier`, converted to an int (fractional part truncated).

        Returns:
            int: Total experience points after bonus.
        """
        return int(self.experience_points * self.bonus_multiplier)

    def with_bonus(self, multiplier: float) -> "QuestReward":
        """
        Return a new QuestReward with its bonus_multiplier multiplied by the given multiplier.

        Parameters:
            multiplier (float): Factor to apply to the existing bonus multiplier (must be >= 0).

        Returns:
            QuestReward: A new instance with the same experience_points and an updated bonus_multiplier.
        """
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
        """
        Validate QuestDeadline invariant: ensures buffer_days is non-negative.

        Raises:
            ValueError: If `buffer_days` is negative.
        """
        if self.buffer_days < 0:
            raise ValueError("Buffer days cannot be negative")

    @property
    def effective_deadline(self) -> date:
        """
        Return the effective deadline adjusted by the buffer days.

        The effective deadline is computed as self.due_date minus self.buffer_days days.

        Returns:
            date: The adjusted deadline (due_date - buffer_days).
        """
        return self.due_date - timedelta(days=self.buffer_days)

    def is_overdue(self, current_date: Optional[date] = None) -> bool:
        """
        Return True if the deadline's due_date is strictly before the given current_date.

        If current_date is omitted, today's date is used.

        Parameters:
            current_date (Optional[date]): Date to compare against the deadline. Defaults to today's date.

        Returns:
            bool: True when current_date > due_date (deadline passed), otherwise False.
        """
        if current_date is None:
            current_date = date.today()
        return current_date > self.due_date

    def is_approaching(
        self, warning_days: int = 3, current_date: Optional[date] = None
    ) -> bool:
        """
        Return True if the deadline is within the given warning period and not yet overdue.

        If current_date is omitted, today's date is used. The warning period is measured
        relative to the effective deadline (due_date minus buffer_days).

        Parameters:
            warning_days (int): Number of days before the effective deadline that should
                be considered the warning window (default 3).
            current_date (Optional[date]): Date to evaluate against (default: today).

        Returns:
            bool: True when current_date is on or after (effective_deadline - warning_days)
            and strictly before the due date; otherwise False.
        """
        if current_date is None:
            current_date = date.today()

        warning_date = self.effective_deadline - timedelta(days=warning_days)
        return current_date >= warning_date and not self.is_overdue(current_date)

    def days_remaining(self, current_date: Optional[date] = None) -> int:
        """
        Return the number of whole days from `current_date` (default: today) until the deadline.

        If the deadline has passed, the result will be negative (overdue).

        Parameters:
            current_date (Optional[date]): Reference date for the calculation; defaults to `date.today()`.

        Returns:
            int: Days until `due_date` (negative if overdue).
        """
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
        """
        Validate HabitStreak invariants after initialization.

        Ensures `current_count` and `longest_count` are non-negative and that `current_count`
        does not exceed `longest_count`. Raises ValueError if any invariant is violated.
        """
        if self.current_count < 0:
            raise ValueError("Current streak count cannot be negative")
        if self.longest_count < 0:
            raise ValueError("Longest streak count cannot be negative")
        if self.current_count > self.longest_count:
            raise ValueError("Current streak cannot be longer than longest streak")

    def is_active(self, current_date: Optional[date] = None) -> bool:
        """
        Return True if the habit streak is currently considered active.

        A streak is active when `current_count` > 0, `last_completion_date` is set, and the elapsed
        time since `last_completion_date` does not exceed the allowed gap for the streak's type:
        - DAILY: <= 1 day
        - WEEKLY: <= 7 days
        - MONTHLY: <= 31 days

        Parameters:
            current_date (Optional[date]): Reference date used to evaluate the streak; defaults to today.

        Returns:
            bool: True if the streak is active, False otherwise.
        """
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
        """
        Extend the habit streak with a new completion date and return an updated HabitStreak.

        If the current streak is inactive for the given completion_date, this starts a new streak (current_count=1) and updates longest_count if needed. If active, increments current_count by one and updates longest_count to the new maximum. Does not modify the original instance.

        Parameters:
            completion_date (date): Date of the new completion used to determine activity and set last_completion_date.

        Returns:
            HabitStreak: A new frozen HabitStreak reflecting the extended or restarted streak.
        """
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
        """
        Return a new HabitStreak representing a broken streak.

        The returned HabitStreak has current_count set to 0 and preserves longest_count,
        streak_type, and last_completion_date from the original instance.
        """
        return HabitStreak(
            current_count=0,
            longest_count=self.longest_count,
            streak_type=self.streak_type,
            last_completion_date=self.last_completion_date,
        )

    def get_milestone_level(self) -> Optional[str]:
        """
        Return the milestone level name corresponding to the current streak length.

        Returns:
            Optional[str]: One of `"legendary"`, `"master"`, `"expert"`, `"advanced"`, `"intermediate"`, or `"beginner"` when `current_count` meets the respective thresholds (365, 180, 90, 30, 14, 7). Returns `None` if the streak is shorter than 7.
        """
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
        """
        Validate that completion_percentage is within the inclusive range [0, 100].

        Runs after dataclass initialization and raises ValueError if completion_percentage is outside the allowed range.
        """
        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

    def is_complete(self) -> bool:
        """Check if quest is complete."""
        return self.completion_percentage >= 100.0

    def update_progress(self, new_percentage: float) -> "QuestProgress":
        """
        Return a new QuestProgress with an updated completion percentage.

        Validates that `new_percentage` is within [0, 100]; returns a new immutable
        QuestProgress preserving the existing `milestones_completed`.

        Raises:
            ValueError: If `new_percentage` is outside the 0–100 range.
        """
        if not 0 <= new_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        return QuestProgress(
            completion_percentage=new_percentage,
            milestones_completed=self.milestones_completed,
        )

    def add_milestone(self, milestone: str) -> "QuestProgress":
        """
        Add a milestone to the progress and return an updated QuestProgress.

        If the milestone already exists, the original QuestProgress is returned (no change).
        The returned object preserves the current completion_percentage and appends the new
        milestone to milestones_completed in a new QuestProgress instance.

        Parameters:
            milestone (str): Identifier or name of the milestone to add.

        Returns:
            QuestProgress: A new QuestProgress with the milestone added, or self if the milestone was already present.
        """
        if milestone in self.milestones_completed:
            return self  # Milestone already exists

        new_milestones = self.milestones_completed + [milestone]
        return QuestProgress(
            completion_percentage=self.completion_percentage,
            milestones_completed=new_milestones,
        )

    def get_progress_level(self) -> str:
        """
        Return a short descriptive level for the current completion percentage.

        Maps completion_percentage to one of: "complete" (>=100), "nearly_complete" (>=75), "halfway" (>=50),
        "started" (>=25), or "not_started" (<25).

        Returns:
            str: One of the five progress level strings above.
        """
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
        """
        Validate HabitSchedule invariants after initialization.

        Ensures `frequency_days` and `target_count_per_period` are positive integers; raises ValueError if either is non‑positive.
        """
        if self.frequency_days <= 0:
            raise ValueError("Frequency days must be positive")
        if self.target_count_per_period <= 0:
            raise ValueError("Target count must be positive")

    def is_due(
        self, last_completion: Optional[date], current_date: Optional[date] = None
    ) -> bool:
        """
        Return True when the habit is due to be completed according to this schedule.

        If `last_completion` is None the habit is considered due. `current_date` defaults to today.
        For flexible scheduling the habit becomes due when the number of days since the last completion
        is greater than or equal to `frequency_days - 1`; for strict scheduling it becomes due when
        that difference is greater than or equal to `frequency_days`.

        Parameters:
            last_completion (Optional[date]): Date of the last completion, or None if never completed.
            current_date (Optional[date]): Date to evaluate against (defaults to today).

        Returns:
            bool: True if the habit is due on `current_date`, False otherwise.
        """
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
        """
        Return the next due date for the habit.

        If last_completion is None, returns today's date. Otherwise returns last_completion plus the schedule's frequency_days.
        """
        if not last_completion:
            return date.today()

        return last_completion + timedelta(days=self.frequency_days)

    def completion_window_days(self) -> int:
        """
        Return the number of days allowed to complete the habit in the current schedule.

        For flexible scheduling this is half the configured frequency (integer division) with a minimum of 1 day.
        For strict scheduling this is always 1.

        Returns:
            int: completion window size in days.
        """
        if self.flexible_scheduling:
            return max(1, self.frequency_days // 2)
        else:
            return 1
