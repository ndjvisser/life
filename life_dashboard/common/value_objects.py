"""Shared kernel value objects reused across multiple bounded contexts."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserId:
    """User identifier value object shared across contexts."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("User ID must be positive")


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
            raise ValueError(
                f"Experience reward cannot exceed {self.max_value}"
            )
