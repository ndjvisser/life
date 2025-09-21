"""
Quest Domain Value Objects

Immutable value objects that encapsulate domain constraints and validation.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass

from life_dashboard.common.value_objects import ExperienceReward, UserId

__all__ = [
    "QuestId",
    "QuestTitle",
    "QuestDescription",
    "HabitId",
    "HabitName",
    "StreakCount",
    "CompletionCount",
    "ExperienceReward",
    "UserId",
    "QuestProgress",
]


@dataclass(frozen=True)
class QuestId:
    """Quest identifier value object supporting string or integer identifiers."""

    value: int | str

    def __post_init__(self) -> None:
        normalized = self._normalize(self.value)
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(value: object) -> int | str:
        """Normalize quest identifiers to a positive int or non-empty string."""

        if isinstance(value, QuestId):
            return value.value

        if isinstance(value, bool):
            raise ValueError("Quest ID cannot be a boolean value")

        if isinstance(value, int):
            if value <= 0:
                raise ValueError("Quest ID must be positive")
            return value

        if isinstance(value, str):
            text_value = value.strip()
            if not text_value:
                raise ValueError("Quest ID cannot be empty")

            if text_value.isdigit():
                numeric_value = int(text_value)
                if numeric_value <= 0:
                    raise ValueError("Quest ID must be positive")
                return numeric_value

            return text_value

        raise TypeError(f"Unsupported Quest ID type: {type(value).__name__}")

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple delegation
        if isinstance(other, QuestId):
            return self.value == other.value
        if isinstance(other, int | str):
            try:
                return self.value == self._normalize(other)
            except ValueError:
                return False
        return False

    def __hash__(self) -> int:  # pragma: no cover - delegation to underlying value
        return hash(self.value)

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return str(self.value)


@dataclass(frozen=True)
class QuestTitle:
    """Quest title value object with validation"""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Quest title cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Quest title cannot exceed 200 characters")

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple comparison
        if isinstance(other, QuestTitle):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:  # pragma: no cover - delegation to underlying value
        return hash(self.value)

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.value


@dataclass(frozen=True)
class QuestDescription:
    """Quest description value object"""

    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 1000:
            raise ValueError("Quest description cannot exceed 1000 characters")

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple comparison
        if isinstance(other, QuestDescription):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:  # pragma: no cover - delegation to underlying value
        return hash(self.value)

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.value


@dataclass(frozen=True)
class HabitId:
    """Habit identifier value object"""

    value: int

    def __post_init__(self):
        if isinstance(self.value, bool):
            raise ValueError("Habit ID cannot be a boolean value")
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
        if isinstance(self.value, bool):
            raise ValueError("Streak count cannot be a boolean value")
        if self.value < 0:
            raise ValueError("Streak count cannot be negative")
        if self.value > 10000:  # Reasonable upper limit
            raise ValueError("Streak count cannot exceed 10000")


@dataclass(frozen=True)
class CompletionCount:
    """Completion count value object with validation"""

    value: int

    def __post_init__(self):
        if isinstance(self.value, bool):
            raise ValueError("Completion count cannot be a boolean value")
        if self.value < 0:
            raise ValueError("Completion count cannot be negative")
        if self.value > 1000:  # Reasonable daily limit
            raise ValueError("Completion count cannot exceed 1000")


@dataclass(frozen=True)
class QuestProgress:
    """Value object for quest progress tracking."""

    completion_percentage: float
    milestones_completed: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.completion_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")
        object.__setattr__(
            self, "milestones_completed", tuple(self.milestones_completed)
        )

    def is_complete(self) -> bool:
        """Check if quest is complete."""

        return self.completion_percentage >= 100.0

    def update_progress(self, new_percentage: float) -> "QuestProgress":
        """Create new progress with updated percentage."""

        if not 0 <= new_percentage <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")

        return self.__class__(
            completion_percentage=new_percentage,
            milestones_completed=self.milestones_completed,
        )

    def add_milestone(self, milestone: str) -> "QuestProgress":
        """Create new progress with added milestone."""

        if milestone in self.milestones_completed:
            return self  # Milestone already exists

        return self.__class__(
            completion_percentage=self.completion_percentage,
            milestones_completed=self.milestones_completed + (milestone,),
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
