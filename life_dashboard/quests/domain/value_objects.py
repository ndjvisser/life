"""
Quest Domain Value Objects

Immutable value objects that encapsulate domain constraints and validation.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass


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

        if isinstance(value, int):
            if value <= 0:
                raise ValueError("Quest ID must be positive")
            return value

        if isinstance(value, str):
            text_value = value.strip()
        else:
            text_value = str(value).strip()
        if not text_value:
            raise ValueError("Quest ID cannot be empty")

        if text_value.isdigit():
            numeric_value = int(text_value)
            if numeric_value <= 0:
                raise ValueError("Quest ID must be positive")
            return numeric_value

        return text_value

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple delegation
        if isinstance(other, QuestId):
            return self.value == other.value
        if isinstance(other, (int, str)):
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
class UserId:
    """User identifier value object"""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("User ID must be positive")

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple comparison
        if isinstance(other, UserId):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            try:
                return self.value == int(other)
            except ValueError:
                return False
        return False

    def __hash__(self) -> int:  # pragma: no cover - delegation to underlying value
        return hash(self.value)

    def __int__(self) -> int:  # pragma: no cover - trivial conversion helper
        return self.value

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
        if len(self.value) > 2000:
            raise ValueError("Quest description cannot exceed 2000 characters")

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
class ExperienceReward:
    """Experience reward value object with validation"""

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Experience reward cannot be negative")
        if self.value > 10000:
            raise ValueError("Experience reward cannot exceed 10000")

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple comparison
        if isinstance(other, ExperienceReward):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            try:
                return self.value == int(other)
            except ValueError:
                return False
        return False

    def __hash__(self) -> int:  # pragma: no cover - delegation to underlying value
        return hash(self.value)

    def __int__(self) -> int:  # pragma: no cover - trivial conversion helper
        return self.value

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return str(self.value)


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
