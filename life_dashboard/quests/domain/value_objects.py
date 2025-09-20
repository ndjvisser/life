"""
Quest Domain Value Objects

Immutable value objects that encapsulate domain constraints and validation.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass

from life_dashboard.common.value_objects import ExperienceReward, UserId


@dataclass(frozen=True)
class QuestId:
    """Quest identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quest ID must be positive")


@dataclass(frozen=True)
class QuestTitle:
    """Quest title value object with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Quest title cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Quest title cannot exceed 200 characters")


@dataclass(frozen=True)
class QuestDescription:
    """Quest description value object"""

    value: str

    def __post_init__(self):
        if len(self.value) > 2000:
            raise ValueError("Quest description cannot exceed 2000 characters")


@dataclass(frozen=True)
class HabitId:
    """Habit identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Habit ID must be positive")


@dataclass(frozen=True)
class HabitName:
    """Habit name value object with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Habit name cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Habit name cannot exceed 100 characters")


@dataclass(frozen=True)
class StreakCount:
    """Streak count value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Streak count cannot be negative")
        if self.value > 10000:  # Reasonable upper limit
            raise ValueError("Streak count cannot exceed 10000")


@dataclass(frozen=True)
class CompletionCount:
    """Completion count value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Completion count cannot be negative")
        if self.value > 1000:  # Reasonable daily limit
            raise ValueError("Completion count cannot exceed 1000")
