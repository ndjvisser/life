"""
Skills domain entities - pure Python business logic without Django dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


@dataclass
class SkillCategory:
    """Pure domain entity for skill categories."""

    category_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    icon: str = ""

    def __post_init__(self):
        if not self.name:
            raise ValueError("Category name is required")


@dataclass
class Skill:
    """Pure domain entity for skill tracking."""

    skill_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    category_id: str = ""
    name: str = ""
    description: str = ""

    # Progress tracking
    level: int = 1
    experience_points: int = 0
    experience_to_next_level: int = 1000

    # Metadata
    created_at: Optional[datetime] = None
    last_practiced: Optional[datetime] = None

    def __post_init__(self):
        """Validate skill on creation."""
        if not self.name:
            raise ValueError("Skill name is required")

        if self.level < 1:
            raise ValueError("Skill level must be at least 1")

        if self.experience_points < 0:
            raise ValueError("Experience points cannot be negative")

    def add_experience(self, amount: int) -> Tuple[int, bool]:
        """
        Add experience points and handle leveling up.

        Returns:
            tuple: (new_level, level_up_occurred)
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
        """Handle leveling up logic."""
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
        """Get progress percentage towards next level."""
        if self.experience_to_next_level == 0:
            return 100.0

        return min(
            100.0, (self.experience_points / self.experience_to_next_level) * 100
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
