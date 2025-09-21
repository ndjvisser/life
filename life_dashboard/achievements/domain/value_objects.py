"""Value objects for achievements domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserIdentifier:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("User identifier must be positive")


@dataclass(frozen=True)
class AchievementIdentifier:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Achievement identifier cannot be empty")


@dataclass(frozen=True)
class AchievementProgress:
    """Represents tracked progress toward an achievement."""

    name: str
    description: str
    tier: str
    current_progress: int
    target_progress: int
    reward_points: int
    potential_reward: Optional[int]

    def __post_init__(self) -> None:
        if self.current_progress < 0:
            raise ValueError("Progress cannot be negative")
        if self.target_progress <= 0:
            raise ValueError("Target must be positive")
        if self.reward_points < 0:
            raise ValueError("Reward points cannot be negative")
        if self.potential_reward is not None and self.potential_reward < 0:
            raise ValueError("Potential reward cannot be negative")

    @property
    def completion_percentage(self) -> float:
        percentage = (self.current_progress / self.target_progress) * 100
        return max(0.0, min(100.0, percentage))

    @property
    def remaining_progress(self) -> int:
        return max(0, self.target_progress - self.current_progress)
