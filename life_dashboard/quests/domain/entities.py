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
        """Validate quest on creation."""
        if not self.title:
            raise ValueError("Quest title is required")

        if self.experience_reward < 0:
            raise ValueError("Experience reward cannot be negative")

        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        if self.due_date and self.start_date and self.due_date < self.start_date:
            raise ValueError("Due date cannot be before start date")

    def start_quest(self) -> None:
        """Start the quest."""
        if self.status != QuestStatus.DRAFT:
            raise ValueError(f"Cannot start quest in {self.status.value} status")

        self.status = QuestStatus.ACTIVE
        if not self.start_date:
            self.start_date = date.today()
        self.updated_at = datetime.utcnow()

    def complete_quest(self) -> Tuple[int, datetime]:
        """
        Complete the quest.

        Returns:
            tuple: (experience_reward, completion_timestamp)
        """
        if self.status != QuestStatus.ACTIVE:
            raise ValueError(f"Cannot complete quest in {self.status.value} status")

        self.status = QuestStatus.COMPLETED
        self.completion_percentage = 100.0
        self.completed_at = datetime.utcnow()
        self.updated_at = self.completed_at

        return self.experience_reward, self.completed_at

    def fail_quest(self, reason: str = "") -> None:
        """Mark quest as failed."""
        if self.status not in [QuestStatus.ACTIVE, QuestStatus.PAUSED]:
            raise ValueError(f"Cannot fail quest in {self.status.value} status")

        self.status = QuestStatus.FAILED
        self.updated_at = datetime.utcnow()

    def pause_quest(self) -> None:
        """Pause an active quest."""
        if self.status != QuestStatus.ACTIVE:
            raise ValueError(f"Cannot pause quest in {self.status.value} status")

        self.status = QuestStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def resume_quest(self) -> None:
        """Resume a paused quest."""
        if self.status != QuestStatus.PAUSED:
            raise ValueError(f"Cannot resume quest in {self.status.value} status")

        self.status = QuestStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def update_progress(self, percentage: float) -> None:
        """Update quest completion percentage."""
        if not 0 <= percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        if self.status != QuestStatus.ACTIVE:
            raise ValueError(
                f"Cannot update progress for quest in {self.status.value} status"
            )

        self.completion_percentage = percentage
        self.updated_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        """Check if quest is overdue."""
        if not self.due_date or self.status in [
            QuestStatus.COMPLETED,
            QuestStatus.FAILED,
        ]:
            return False

        return date.today() > self.due_date

    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date."""
        if not self.due_date:
            return None

        delta = self.due_date - date.today()
        return delta.days

    def can_be_completed(self) -> bool:
        """Check if quest can be completed (prerequisites met)."""
        # For now, just check status - prerequisite checking would be handled by service
        return self.status == QuestStatus.ACTIVE

    def get_difficulty_multiplier(self) -> float:
        """Get experience multiplier based on difficulty."""
        multipliers = {
            QuestDifficulty.EASY: 0.8,
            QuestDifficulty.MEDIUM: 1.0,
            QuestDifficulty.HARD: 1.5,
            QuestDifficulty.LEGENDARY: 2.0,
        }
        return multipliers.get(self.difficulty, 1.0)

    def calculate_final_experience(self) -> int:
        """Calculate final experience reward with difficulty multiplier."""
        base_reward = self.experience_reward
        multiplier = self.get_difficulty_multiplier()
        return int(base_reward * multiplier)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
        """Validate habit on creation."""
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
        Complete habit for a specific date.

        Args:
            completion_date: Date of completion (defaults to today)

        Returns:
            tuple: (experience_gained, new_streak, streak_milestone_reached)
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
        Break the current streak.

        Returns:
            The streak that was broken
        """
        broken_streak = self.current_streak
        self.current_streak = 0
        self.updated_at = datetime.utcnow()

        return broken_streak

    def _is_streak_continued(self, completion_date: date) -> bool:
        """Check if completion continues the current streak."""
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
        """Calculate experience reward with streak bonuses."""
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
        """Check if current streak reached a milestone."""
        milestones = [7, 14, 21, 30, 60, 90, 180, 365]
        return self.current_streak in milestones

    def get_completion_rate(self, days: int = 30) -> float:
        """Calculate completion rate over the last N days."""
        # This would need completion history data - simplified for now
        if self.current_streak >= days:
            return 100.0

        return (self.current_streak / days) * 100.0

    def is_due_today(self) -> bool:
        """Check if habit is due today based on frequency."""
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
        """Convert to dictionary representation."""
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
        """Validate completion on creation."""
        if not self.habit_id:
            raise ValueError("Habit ID is required")

        if self.count <= 0:
            raise ValueError("Completion count must be positive")

        if self.experience_gained < 0:
            raise ValueError("Experience gained cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
