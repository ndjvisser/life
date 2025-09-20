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
        Add positive experience points to the profile, update the level, and indicate if a level-up occurred.

        Points are validated as a positive integer and accumulated up to a hard cap (2**31 - 1) to prevent overflow. Level is recomputed as max(1, (experience_points // 1000) + 1) — i.e., 1000 XP per level.

        Args:
            points (int): Positive experience points to add.

        Returns:
            Tuple[int, bool]: (new_level, level_up_occurred) where `level_up_occurred` is True if the level increased.

        Raises:
            ValueError: If `points` is not a positive integer.
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
        """
        Update allowed profile fields from keyword arguments.

        Only the following fields may be updated: 'first_name', 'last_name', 'email', 'bio', 'location', and 'birth_date'.
        Each provided allowed field is assigned directly to the corresponding attribute on the instance.
        If any keyword name is not in the allowed set a ValueError is raised and no further fields are processed.
        """
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
        """
        Return the user's full name by concatenating first_name and last_name, trimmed of surrounding whitespace.
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def experience_to_next_level(self) -> int:
        """
        Return the remaining experience points required to reach the next level.

        Calculates the next-level threshold as `level * 1000` and returns the non-negative difference
        between that threshold and the current `experience_points`. Result is floored at 0 (already at
        or above next level yields 0).
        """
        next_level_threshold = self.level * 1000
        return max(0, next_level_threshold - self.experience_points)

    @property
    def level_progress_percentage(self) -> float:
        """
        Return the user's progress toward the next level as a percentage.

        Calculates progress using 1000 XP per level: the percentage of experience gained
        within the current level's range. The result is capped at 100.0. If the
        computed level range is zero (shouldn't occur in normal progression), returns
        100.0.
        """
        current_level_threshold = (self.level - 1) * 1000
        next_level_threshold = self.level * 1000
        level_experience = self.experience_points - current_level_threshold
        level_range = next_level_threshold - current_level_threshold

        if level_range == 0:
            return 100.0

        return min(100.0, (level_experience / level_range) * 100)
