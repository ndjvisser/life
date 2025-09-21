"""Value objects used by the skills domain services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SkillIdentifier:
    """Strongly typed identifier for a skill."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Skill identifier cannot be empty")


@dataclass(frozen=True)
class UserIdentifier:
    """Strongly typed identifier for the user owner of a skill."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("User identifier must be positive")


@dataclass(frozen=True)
class PracticeSession:
    """Representation of a single practice session for a skill."""

    skill_id: SkillIdentifier
    practiced_at: datetime
    experience_gained: int

    def __post_init__(self) -> None:
        if self.experience_gained < 0:
            raise ValueError("Experience gained cannot be negative")


@dataclass(frozen=True)
class SkillProgress:
    """Represents the progress a skill has made towards the next milestone."""

    current_level: int
    experience_points: int
    experience_to_next_level: int
    progress_points: int
    last_practiced: Optional[datetime]

    def __post_init__(self) -> None:
        if self.current_level < 0:
            raise ValueError("Skill level cannot be negative")
        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")
        if self.experience_to_next_level <= 0:
            raise ValueError("Experience to next level must be positive")
        if self.progress_points < 0:
            raise ValueError("Progress points cannot be negative")

    def next_milestone(self, milestone_interval: int = 5) -> int:
        """Return the next milestone level for the skill."""

        remainder = self.current_level % milestone_interval
        if remainder == 0:
            return self.current_level + milestone_interval
        return self.current_level + (milestone_interval - remainder)

    def progress_percentage(self, additional_progress: int = 0) -> float:
        """Return the progress percentage including extra experience."""

        total_progress = self.progress_points + max(additional_progress, 0)
        percentage = (total_progress / self.experience_to_next_level) * 100
        return max(0.0, min(100.0, percentage))

    def days_since_practice(self, reference: datetime) -> Optional[int]:
        """Return the number of days since the skill was last practiced."""

        if self.last_practiced is None:
            return None
        delta = reference - self.last_practiced
        return max(0, delta.days)
