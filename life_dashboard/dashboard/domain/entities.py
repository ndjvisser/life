"""
Dashboard domain entities - pure Python business logic without Django dependencies.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Tuple


@dataclass
class UserProfile:
    """Pure domain entity for user profile data."""

    user_id: int
    username: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    bio: str = ""
    location: str = ""
    birth_date: Optional[date] = None
    experience_points: int = 0
    level: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def add_experience(self, points: int) -> Tuple[int, bool]:
        """
        Add experience points and calculate level.

        Args:
            points: Experience points to add (must be positive)

        Returns:
            tuple: (new_level, level_up_occurred)

        Raises:
            ValueError: If points is not a positive integer
        """
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Experience points must be a positive integer.")

        # Cap experience points to prevent overflow
        max_experience = 2**31 - 1
        old_level = self.level

        if self.experience_points + points > max_experience:
            self.experience_points = max_experience
        else:
            self.experience_points += points

        # Calculate new level: 1000 XP per level, minimum level 1
        self.level = max(1, (self.experience_points // 1000) + 1)

        level_up_occurred = self.level > old_level
        return self.level, level_up_occurred

    def update_profile(self, **kwargs) -> None:
        """Update profile fields with validation."""
        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "bio",
            "location",
            "birth_date",
        }

        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(self, field, value)
            else:
                raise ValueError(f"Field '{field}' is not allowed to be updated")

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def experience_to_next_level(self) -> int:
        """Calculate experience needed for next level."""
        next_level_threshold = self.level * 1000
        return max(0, next_level_threshold - self.experience_points)

    @property
    def level_progress_percentage(self) -> float:
        """Calculate progress percentage towards next level."""
        current_level_threshold = (self.level - 1) * 1000
        next_level_threshold = self.level * 1000
        level_experience = self.experience_points - current_level_threshold
        level_range = next_level_threshold - current_level_threshold

        if level_range == 0:
            return 100.0

        return min(100.0, (level_experience / level_range) * 100)
