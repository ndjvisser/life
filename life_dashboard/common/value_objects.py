"""Shared kernel value objects reused across multiple bounded contexts."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserId:
    """User identifier value object shared across contexts."""

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
class ExperienceReward:
    """Experience reward value object with configurable upper bound."""

    value: int
    max_value: int = field(default=10000, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Experience reward cannot be negative")
        if self.max_value <= 0:
            raise ValueError("Maximum experience reward must be positive")
        if self.value > self.max_value:
            raise ValueError(f"Experience reward cannot exceed {self.max_value}")

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
