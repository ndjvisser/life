"""
Dashboard domain value objects - immutable objects that represent concepts.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OnboardingState(Enum):
    """User onboarding states."""

    REGISTRATION = "registration"
    PROFILE_SETUP = "profile_setup"
    INITIAL_GOALS = "initial_goals"
    DASHBOARD = "dashboard"


@dataclass(frozen=True)
class ExperiencePoints:
    """Value object for experience points with validation."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Experience points must be an integer")
        if self.value < 0:
            raise ValueError("Experience points cannot be negative")
        if self.value > 2**31 - 1:
            raise ValueError("Experience points exceed maximum value")

    def add(self, points: int) -> "ExperiencePoints":
        """Add points and return new ExperiencePoints object."""
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Points to add must be a positive integer")

        new_value = min(self.value + points, 2**31 - 1)
        return ExperiencePoints(new_value)

    def calculate_level(self) -> int:
        """Calculate level based on experience points."""
        return max(1, (self.value // 1000) + 1)


@dataclass(frozen=True)
class UserLevel:
    """Value object for user level with validation."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Level must be an integer")
        if self.value < 1:
            raise ValueError("Level must be at least 1")
        if self.value > 1000:  # Reasonable maximum
            raise ValueError("Level exceeds maximum value")

    @classmethod
    def from_experience(cls, experience_points: int) -> "UserLevel":
        """Create UserLevel from experience points."""
        level = max(1, (experience_points // 1000) + 1)
        return cls(level)

    def experience_threshold(self) -> int:
        """Get experience threshold for this level."""
        return (self.value - 1) * 1000

    def next_level_threshold(self) -> int:
        """Get experience threshold for next level."""
        return self.value * 1000


@dataclass(frozen=True)
class ProfileUpdateData:
    """Value object for profile update data with validation."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[str] = None  # ISO date string

    def __post_init__(self):
        # Validate string lengths
        if self.first_name is not None and len(self.first_name) > 150:
            raise ValueError("First name too long")
        if self.last_name is not None and len(self.last_name) > 150:
            raise ValueError("Last name too long")
        if self.email is not None and len(self.email) > 254:
            raise ValueError("Email too long")
        if self.bio is not None and len(self.bio) > 500:
            raise ValueError("Bio too long")
        if self.location is not None and len(self.location) > 30:
            raise ValueError("Location too long")

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
