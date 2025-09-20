"""
Dashboard domain value objects - immutable objects that represent concepts.
"""

from dataclasses import dataclass
from enum import Enum


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
        """
        Validate the ExperiencePoints.value invariant after dataclass initialization.

        Ensures `value` is an integer, non-negative, and does not exceed 2**31 - 1.

        Raises:
            ValueError: If `value` is not an int, is negative, or is greater than 2**31 - 1.
        """
        if not isinstance(self.value, int):
            raise ValueError("Experience points must be an integer")
        if self.value < 0:
            raise ValueError("Experience points cannot be negative")
        if self.value > 2**31 - 1:
            raise ValueError("Experience points exceed maximum value")

    def add(self, points: int) -> "ExperiencePoints":
        """
        Return a new ExperiencePoints representing this value plus the given points.

        Parameters:
            points (int): Positive number of points to add.

        Returns:
            ExperiencePoints: New instance with the increased value; result is capped at 2**31 - 1.

        Raises:
            ValueError: If `points` is not a positive integer.
        """
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Points to add must be a positive integer")

        new_value = min(self.value + points, 2**31 - 1)
        return ExperiencePoints(new_value)

    def calculate_level(self) -> int:
        """
        Return the user level derived from experience points.

        Level is computed as (value // 1000) + 1 and is at minimum 1.

        Returns:
            int: Calculated level.
        """
        return max(1, (self.value // 1000) + 1)


@dataclass(frozen=True)
class UserLevel:
    """Value object for user level with validation."""

    value: int

    def __post_init__(self):
        """
        Validate invariants for a UserLevel instance.

        Ensures the `value` field is an integer between 1 and 1000 inclusive.
        Raises ValueError if `value` is not an int, is less than 1, or exceeds 1000.
        """
        if not isinstance(self.value, int):
            raise ValueError("Level must be an integer")
        if self.value < 1:
            raise ValueError("Level must be at least 1")
        if self.value > 1000:  # Reasonable maximum
            raise ValueError("Level exceeds maximum value")

    @classmethod
    def from_experience(cls, experience_points: int) -> "UserLevel":
        """
        Create a UserLevel from total experience points.

        Computes level as max(1, (experience_points // 1000) + 1) where each 1000 points increases the level by one, then returns a UserLevel instance for that level.

        Parameters:
            experience_points (int): Total accumulated experience points.

        Returns:
            UserLevel: Instance representing the derived level.
        """
        level = max(1, (experience_points // 1000) + 1)
        return cls(level)

    def experience_threshold(self) -> int:
        """
        Return the inclusive minimum experience points required for this level.

        For level N this is (N - 1) * 1000; for level 1 this returns 0.

        Returns:
            int: Inclusive lower experience threshold (number of experience points).
        """
        return (self.value - 1) * 1000

    def next_level_threshold(self) -> int:
        """
        Return the cumulative experience required to reach the next level.

        Returns:
            int: Experience point threshold for the next level (current level value * 1000).
        """
        return self.value * 1000


@dataclass(frozen=True)
class ProfileUpdateData:
    """Value object for profile update data with validation."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    bio: str | None = None
    location: str | None = None
    birth_date: str | None = None  # ISO date string

    def __post_init__(self):
        # Validate string lengths
        """
        Validate field length invariants for ProfileUpdateData.

        Ensures optional string fields do not exceed their maximum allowed lengths:
        - first_name, last_name: max 150 characters
        - email: max 254 characters
        - bio: max 500 characters
        - location: max 30 characters

        Raises:
            ValueError: if any provided field is longer than its allowed maximum.
        """
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
        """
        Return a dictionary of the instance's fields excluding any with value None.

        The returned dict maps attribute names to their values and is a shallow copy of the instance state; attributes with value None are omitted.
        Returns:
            dict: Mapping of field names to their non-None values.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}
