"""
Skills domain entities - pure Python business logic without Django dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class SkillCategory:
    """Pure domain entity for skill categories."""

    category_id: str | None = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    icon: str = ""

    def __post_init__(self):
        """
        Validate the dataclass after initialization.

        Ensures the category has a non-empty `name`; raises ValueError if the name is missing or empty.
        """
        if not self.name:
            raise ValueError("Category name is required")


@dataclass
class Skill:
    """Pure domain entity for skill tracking."""

    skill_id: str | None = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    category_id: str = ""
    name: str = ""
    description: str = ""

    # Progress tracking
    level: int = 1
    experience_points: int = 0
    experience_to_next_level: int = 1000

    # Metadata
    created_at: datetime | None = None
    last_practiced: datetime | None = None

    def __post_init__(self):
        """
        Validate Skill fields after initialization.

        Ensures the required invariants for a newly created Skill:
        - `name` must be non-empty.
        - `level` must be at least 1.
        - `experience_points` must not be negative.

        Raises:
            ValueError: If any validation fails.
        """
        if not self.name:
            raise ValueError("Skill name is required")

        if self.level < 1:
            raise ValueError("Skill level must be at least 1")

        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")

    def add_experience(self, amount: int) -> tuple[int, bool]:
        """
        Add experience to the skill, update timestamps, and handle level ups.

        Parameters:
            amount (int): Positive number of experience points to add; raises ValueError if <= 0.

        Returns:
            Tuple[int, bool]: (current_level, level_up_occurred) where `level_up_occurred` is True if the skill's level increased.

        Notes:
            - Total experience is capped at 2^31 - 1 to avoid integer overflow.
            - The method will repeatedly call level_up() while experience meets or exceeds the threshold and the level is below the maximum (100).
            - Updates `last_practiced` to the current UTC time.
        """
        if amount <= 0:
            raise ValueError("Experience amount must be positive")

        old_level = self.level
        max_experience = 2**31 - 1

        # Cap experience points to prevent overflow
        new_experience = min(self.experience_points + amount, max_experience)
        self.experience_points = new_experience

        # Level up if enough experience and not at max level
        max_level = 100
        while (
            self.experience_points >= self.experience_to_next_level
            and self.level < max_level
        ):
            self.level_up()

        self.last_practiced = datetime.utcnow()

        level_up_occurred = self.level > old_level
        return self.level, level_up_occurred

    def level_up(self) -> None:
        """
        Increment the skill's level by one and adjust experience counters.

        If the skill is already at the maximum level (100), this is a no-op.
        Otherwise this method:
        - Increments `level` by 1.
        - Subtracts the current `experience_to_next_level` from `experience_points`.
        - Increases `experience_to_next_level` by 10%, capped at 2**31 - 1 to avoid integer overflow.

        Modifies the instance in place; returns None.
        """
        max_level = 100
        if self.level >= max_level:
            return

        self.level += 1
        self.experience_points -= self.experience_to_next_level
        # Increase experience needed for next level (10% more)
        max_experience = 2**31 - 1
        self.experience_to_next_level = min(
            int(self.experience_to_next_level * 1.1), max_experience
        )

    def get_progress_percentage(self) -> float:
        """
        Return the current progress toward the next level as a percentage.

        If `experience_to_next_level` is zero this returns 100.0. The result is capped at 100.0 and represents
        (experience_points / experience_to_next_level) * 100.
        """
        if self.experience_to_next_level == 0:
            return 100.0

        return min(
            100.0, (self.experience_points / self.experience_to_next_level) * 100
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the Skill suitable for serialization.

        The dictionary includes identifiers, core attributes, derived progress, and ISO-8601 timestamp strings.

        Returns:
            Dict[str, Any]: {
                "skill_id": Optional[str],
                "user_id": int,
                "category_id": str,
                "name": str,
                "description": str,
                "level": int,
                "experience_points": int,
                "experience_to_next_level": int,
                "progress_percentage": float,            # progress toward next level (0.0–100.0)
                "created_at": Optional[str],             # ISO-8601 string or None
                "last_practiced": Optional[str]          # ISO-8601 string or None
            }
        """
        return {
            "skill_id": self.skill_id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "experience_points": self.experience_points,
            "experience_to_next_level": self.experience_to_next_level,
            "progress_percentage": self.get_progress_percentage(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_practiced": self.last_practiced.isoformat()
            if self.last_practiced
            else None,
        }
