"""
Quests domain entities - pure Python business logic without Django dependencies.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class QuestStatus(Enum):
    """Status of a quest."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class QuestType(Enum):
    """Types of quests."""

    LIFE_GOAL = "life_goal"
    ANNUAL_GOAL = "annual_goal"
    MAIN = "main"
    SIDE = "side"
    WEEKLY = "weekly"
    DAILY = "daily"


class QuestDifficulty(Enum):
    """Quest difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"


class HabitFrequency(Enum):
    """Habit frequency patterns."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class Quest:
    """Pure domain entity for quest management."""

    quest_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    title: str = ""
    description: str = ""
    quest_type: QuestType = QuestType.MAIN
    difficulty: QuestDifficulty = QuestDifficulty.MEDIUM
    status: QuestStatus = QuestStatus.DRAFT

    # Rewards and progression
    experience_reward: int = 10
    completion_percentage: float = 0.0

    # Dates
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None

    # Quest chain relationships
    parent_quest_id: Optional[str] = None
    prerequisite_quest_ids: List[str] = field(default_factory=list)

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Perform post-initialization validation for a Quest instance.
        
        Checks performed:
        - title must be non-empty.
        - experience_reward must be >= 0.
        - completion_percentage must be between 0 and 100 inclusive.
        - if both start_date and due_date are provided, due_date must not be earlier than start_date.
        
        Raises:
            ValueError: If any validation rule above is violated.
        """
        if not self.title:
            raise ValueError("Quest title is required")

        if self.experience_reward < 0:
            raise ValueError("Experience reward cannot be negative")

        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        if self.due_date and self.start_date and self.due_date < self.start_date:
            raise ValueError("Due date cannot be before start date")

    def start_quest(self) -> None:
        """
        Transition the quest from DRAFT to ACTIVE and initialize start metadata.
        
        Raises:
            ValueError: If the quest is not in the DRAFT status.
        
        Side effects:
            - Sets self.status to QuestStatus.ACTIVE.
            - If self.start_date is not set, sets it to today's date.
            - Updates self.updated_at to the current UTC datetime.
        """
        if self.status != QuestStatus.DRAFT:
            raise ValueError(f"Cannot start quest in {self.status.value} status")

        self.status = QuestStatus.ACTIVE
        if not self.start_date:
            self.start_date = date.today()
        self.updated_at = datetime.utcnow()

    def complete_quest(self) -> Tuple[int, datetime]:
        """
        Mark the quest as completed and record completion time.
        
        Completes the quest only if its current status is ACTIVE; otherwise raises ValueError.
        On success, sets status to COMPLETED, sets completion_percentage to 100.0,
        records the completion timestamp (UTC) on `completed_at` and `updated_at`, and
        returns the experience reward and the completion timestamp.
        
        Returns:
            Tuple[int, datetime]: (experience_reward, completion_timestamp)
        """
        if self.status != QuestStatus.ACTIVE:
            raise ValueError(f"Cannot complete quest in {self.status.value} status")

        self.status = QuestStatus.COMPLETED
        self.completion_percentage = 100.0
        self.completed_at = datetime.utcnow()
        self.updated_at = self.completed_at

        return self.experience_reward, self.completed_at

    def fail_quest(self, reason: str = "") -> None:
        """
        Mark the quest as failed.
        
        If the quest is currently ACTIVE or PAUSED, sets its status to FAILED and updates updated_at to the current UTC time.
        The optional `reason` parameter is accepted for API compatibility but is not stored or used by this method.
        
        Parameters:
            reason (str): Optional human-readable reason for failing the quest (ignored).
        
        Raises:
            ValueError: If the quest is not in ACTIVE or PAUSED status.
        """
        if self.status not in [QuestStatus.ACTIVE, QuestStatus.PAUSED]:
            raise ValueError(f"Cannot fail quest in {self.status.value} status")

        self.status = QuestStatus.FAILED
        self.updated_at = datetime.utcnow()

    def pause_quest(self) -> None:
        """
        Pause the quest if it is currently ACTIVE.
        
        Sets the quest's status to PAUSED and updates `updated_at` to the current UTC time.
        Raises a ValueError if the quest is not in the ACTIVE status.
        """
        if self.status != QuestStatus.ACTIVE:
            raise ValueError(f"Cannot pause quest in {self.status.value} status")

        self.status = QuestStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def resume_quest(self) -> None:
        """
        Resume a quest that is currently paused.
        
        Sets the quest's status to ACTIVE and updates the quest's updated_at timestamp.
        
        Raises:
            ValueError: if the quest is not in PAUSED status.
        """
        if self.status != QuestStatus.PAUSED:
            raise ValueError(f"Cannot resume quest in {self.status.value} status")

        self.status = QuestStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def update_progress(self, percentage: float) -> None:
        """
        Set the quest's completion percentage.
        
        Updates the quest's completion_percentage and sets updated_at to the current UTC time.
        
        Parameters:
            percentage (float): New completion percentage; must be between 0 and 100 inclusive.
        
        Raises:
            ValueError: If `percentage` is outside 0–100, or if the quest is not in the ACTIVE status.
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        if self.status != QuestStatus.ACTIVE:
            raise ValueError(
                f"Cannot update progress for quest in {self.status.value} status"
            )

        self.completion_percentage = percentage
        self.updated_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        """
        Return True if the quest is past its due date and still active.
        
        Returns:
            bool: False when there is no due_date or the quest status is COMPLETED or FAILED;
                  otherwise True if today's date is strictly after `due_date`.
        """
        if not self.due_date or self.status in [
            QuestStatus.COMPLETED,
            QuestStatus.FAILED,
        ]:
            return False

        return date.today() > self.due_date

    def days_until_due(self) -> Optional[int]:
        """
        Return the number of days from today until the quest's due date.
        
        Returns:
            int: Number of days until `due_date` (can be negative if the due date is in the past).
            None: If `due_date` is not set.
        """
        if not self.due_date:
            return None

        delta = self.due_date - date.today()
        return delta.days

    def can_be_completed(self) -> bool:
        """
        Return True if the quest is in a state that allows completion.
        
        This method currently only verifies the quest's status (returns True when status is QuestStatus.ACTIVE).
        Prerequisite checks and other external completion conditions are intentionally not evaluated here.
        """
        # For now, just check status - prerequisite checking would be handled by service
        return self.status == QuestStatus.ACTIVE

    def get_difficulty_multiplier(self) -> float:
        """
        Return the experience multiplier for this quest's difficulty.
        
        Maps QuestDifficulty to multipliers: EASY=0.8, MEDIUM=1.0, HARD=1.5, LEGENDARY=2.0.
        If the difficulty is not recognized, returns 1.0 as a safe default.
        
        Returns:
            float: Multiplier to apply to the quest's base experience_reward.
        """
        multipliers = {
            QuestDifficulty.EASY: 0.8,
            QuestDifficulty.MEDIUM: 1.0,
            QuestDifficulty.HARD: 1.5,
            QuestDifficulty.LEGENDARY: 2.0,
        }
        return multipliers.get(self.difficulty, 1.0)

    def calculate_final_experience(self) -> int:
        """
        Return the experience reward adjusted by the quest's difficulty multiplier.
        
        The base `experience_reward` is scaled by the quest's difficulty multiplier and converted to an integer.
        
        Returns:
            int: Final experience reward after applying the difficulty multiplier.
        """
        base_reward = self.experience_reward
        multiplier = self.get_difficulty_multiplier()
        return int(base_reward * multiplier)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a serializable dictionary representation of the Quest.
        
        Dates (start_date, due_date, completed_at, created_at, updated_at) are converted to ISO-8601 strings when present; enum fields (quest_type, difficulty, status) use their .value. The result also includes computed/derived fields: is_overdue, days_until_due, and final_experience_reward.
        """
        return {
            "quest_id": self.quest_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "difficulty": self.difficulty.value,
            "status": self.status.value,
            "experience_reward": self.experience_reward,
            "completion_percentage": self.completion_percentage,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "parent_quest_id": self.parent_quest_id,
            "prerequisite_quest_ids": self.prerequisite_quest_ids,
            "is_overdue": self.is_overdue(),
            "days_until_due": self.days_until_due(),
            "final_experience_reward": self.calculate_final_experience(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Habit:
    """Pure domain entity for habit tracking."""

    habit_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    name: str = ""
    description: str = ""
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_count: int = 1

    # Streak tracking
    current_streak: int = 0
    longest_streak: int = 0

    # Rewards
    experience_reward: int = 5

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_completed: Optional[date] = None

    def __post_init__(self):
        """
        Validate the Habit instance after initialization.
        
        Performs basic invariants and raises ValueError on invalid fields:
        - if `name` is empty or falsy,
        - if `target_count` is not a positive integer,
        - if `experience_reward` is negative.
        
        Raises:
            ValueError: When any of the above validation rules fail.
        """
        if not self.name:
            raise ValueError("Habit name is required")

        if self.target_count <= 0:
            raise ValueError("Target count must be positive")

        if self.experience_reward < 0:
            raise ValueError("Experience reward cannot be negative")

    def complete_habit(
        self, completion_date: Optional[date] = None
    ) -> Tuple[int, int, bool]:
        """
        Mark the habit as completed for a given date, update streak counters, and compute experience and milestone status.
        
        Parameters:
            completion_date (date, optional): Date when the habit was completed. Defaults to today.
        
        Returns:
            tuple: (experience_gained: int, current_streak: int, streak_milestone_reached: bool)
        """
        if not completion_date:
            completion_date = date.today()

        # Check if this continues a streak
        streak_continued = self._is_streak_continued(completion_date)

        if streak_continued:
            self.current_streak += 1
        else:
            self.current_streak = 1

        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_completed = completion_date
        self.updated_at = datetime.utcnow()

        # Calculate experience with streak bonus
        experience_gained = self._calculate_experience_with_bonus()

        # Check for streak milestones
        streak_milestone = self._check_streak_milestone()

        return experience_gained, self.current_streak, streak_milestone

    def break_streak(self, break_date: Optional[date] = None) -> int:
        """
        Reset the habit's current streak to zero and return the streak length that was broken.
        
        If provided, `break_date` is accepted for API symmetry but is not used by this implementation.
        The method updates `updated_at` to the current UTC datetime.
        
        Returns:
            int: The length of the streak that was reset.
        """
        broken_streak = self.current_streak
        self.current_streak = 0
        self.updated_at = datetime.utcnow()

        return broken_streak

    def _is_streak_continued(self, completion_date: date) -> bool:
        """
        Return True if a completion on `completion_date` should be considered a continuation of the current streak.
        
        Detailed behavior:
        - Returns False if there is no recorded `last_completed`.
        - DAILY: streak continues if `completion_date` is the same day or the day after `last_completed`.
        - WEEKLY: streak continues if `completion_date` is within 7 days after `last_completed`.
        - MONTHLY: streak continues if `completion_date` is in the same month as `last_completed` or in the immediately following month.
        - For any other frequency values, returns False.
        
        Parameters:
            completion_date (date): The date of the new completion.
        
        Returns:
            bool: True when the new completion continues the streak, False otherwise.
        """
        if not self.last_completed:
            return False

        if self.frequency == HabitFrequency.DAILY:
            # Streak continues if completed yesterday or today
            days_diff = (completion_date - self.last_completed).days
            return days_diff <= 1

        elif self.frequency == HabitFrequency.WEEKLY:
            # Streak continues if within the same week or next week
            days_diff = (completion_date - self.last_completed).days
            return days_diff <= 7

        elif self.frequency == HabitFrequency.MONTHLY:
            # Streak continues if within the same month or next month
            return (
                completion_date.year == self.last_completed.year
                and completion_date.month <= self.last_completed.month + 1
            )

        return False

    def _calculate_experience_with_bonus(self) -> int:
        """
        Return the habit's experience reward including any streak-based bonus.
        
        Calculates and returns the experience to award for a habit completion by applying a multiplier
        based on the current streak:
        - 30+ days: 2.0× (100% bonus)
        - 14–29 days: 1.5× (50% bonus)
        - 7–13 days: 1.25× (25% bonus)
        - below 7 days: base experience (no bonus)
        
        Returns:
            int: The experience amount after applying the streak bonus.
        """
        base_experience = self.experience_reward

        # Streak bonuses
        if self.current_streak >= 30:
            return int(base_experience * 2.0)  # 100% bonus for 30+ days
        elif self.current_streak >= 14:
            return int(base_experience * 1.5)  # 50% bonus for 14+ days
        elif self.current_streak >= 7:
            return int(base_experience * 1.25)  # 25% bonus for 7+ days

        return base_experience

    def _check_streak_milestone(self) -> bool:
        """
        Return True if the habit's current streak matches a predefined milestone.
        
        Checks the habit's current_streak against the milestone set [7, 14, 21, 30, 60, 90, 180, 365] and returns True when current_streak equals one of those values.
        """
        milestones = [7, 14, 21, 30, 60, 90, 180, 365]
        return self.current_streak in milestones

    def get_completion_rate(self, days: int = 30) -> float:
        """
        Return the habit completion rate as a percentage over a rolling window of `days`.
        
        This uses the habit's current_streak as a proxy for actual completion history (when full history is not available): if current_streak >= days the rate is 100.0, otherwise it returns (current_streak / days) * 100.0.
        
        Parameters:
            days (int): Length of the window (in days) used to compute the completion rate. Must be > 0.
        
        Returns:
            float: Completion rate between 0.0 and 100.0.
        """
        # This would need completion history data - simplified for now
        if self.current_streak >= days:
            return 100.0

        return (self.current_streak / days) * 100.0

    def is_due_today(self) -> bool:
        """
        Return whether the habit is due today according to its frequency.
        
        Returns True if the habit has never been completed. For completed habits, uses the system local date to compute days since last completion:
        - DAILY: due when at least 1 day has passed.
        - WEEKLY: due when at least 7 days have passed.
        - MONTHLY: due when at least 30 days have passed.
        
        For frequencies not explicitly handled (e.g., CUSTOM), returns False.
        """
        if not self.last_completed:
            return True

        today = date.today()
        days_since_last = (today - self.last_completed).days

        if self.frequency == HabitFrequency.DAILY:
            return days_since_last >= 1
        elif self.frequency == HabitFrequency.WEEKLY:
            return days_since_last >= 7
        elif self.frequency == HabitFrequency.MONTHLY:
            return days_since_last >= 30

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the Habit suitable for serialization.
        
        The returned dict contains the habit's basic fields plus a few derived values:
        - `frequency` is returned as the enum's `.value`.
        - Date fields (`last_completed`, `created_at`, `updated_at`) are ISO 8601 strings or None.
        - Includes computed fields: `is_due_today` and `completion_rate_30d` (30-day completion rate).
        
        Returns:
            Dict[str, Any]: Serialized habit mapping with keys:
                "habit_id", "user_id", "name", "description", "frequency",
                "target_count", "current_streak", "longest_streak",
                "experience_reward", "last_completed", "is_due_today",
                "completion_rate_30d", "created_at", "updated_at".
        """
        return {
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency.value,
            "target_count": self.target_count,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "experience_reward": self.experience_reward,
            "last_completed": self.last_completed.isoformat()
            if self.last_completed
            else None,
            "is_due_today": self.is_due_today(),
            "completion_rate_30d": self.get_completion_rate(30),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class HabitCompletion:
    """Domain entity for individual habit completions."""

    completion_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    habit_id: str = ""
    user_id: int = 0
    completion_date: date = field(default_factory=date.today)
    count: int = 1
    notes: str = ""
    experience_gained: int = 0
    streak_at_completion: int = 0

    # Metadata
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Validate fields after initialization.
        
        Performs runtime checks and raises ValueError for invalid inputs:
        - habit_id must be provided (non-empty).
        - count must be a positive integer (> 0).
        - experience_gained must be non-negative.
        
        Raises:
            ValueError: If any of the above validations fail.
        """
        if not self.habit_id:
            raise ValueError("Habit ID is required")

        if self.count <= 0:
            raise ValueError("Completion count must be positive")

        if self.experience_gained < 0:
            raise ValueError("Experience gained cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a serializable dictionary representation of this HabitCompletion.
        
        Dates are converted to ISO 8601 strings; `created_at` is None when not set.
        
        Returns:
            Dict[str, Any]: Keys:
                - completion_id (Optional[str])
                - habit_id (str)
                - user_id (int)
                - completion_date (str) — ISO 8601 date
                - count (int)
                - notes (str)
                - experience_gained (int)
                - streak_at_completion (int)
                - created_at (Optional[str]) — ISO 8601 datetime or None
        """
        return {
            "completion_id": self.completion_id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "completion_date": self.completion_date.isoformat(),
            "count": self.count,
            "notes": self.notes,
            "experience_gained": self.experience_gained,
            "streak_at_completion": self.streak_at_completion,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
