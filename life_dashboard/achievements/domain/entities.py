"""
Achievements domain entities - pure Python business logic without Django dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class AchievementTier(Enum):
    """Achievement tiers."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass
class Achievement:
    """Pure domain entity for achievements."""

    achievement_id: str | None = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    tier: AchievementTier = AchievementTier.BRONZE
    icon: str = ""
    experience_reward: int = 0

    # Requirements
    required_level: int = 1
    required_skill_level: int | None = None
    required_quest_completions: int = 0

    def __post_init__(self):
        """
        Validate invariant constraints after Achievement initialization.

        Raises:
            ValueError: If `name` is empty or falsy, or if `experience_reward` is negative.
        """
        if not self.name:
            raise ValueError("Achievement name is required")

        if self.experience_reward < 0:
            raise ValueError("Experience reward cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the Achievement suitable for serialization.

        The mapping includes all dataclass fields. The `tier` is converted to its string value
        (e.g., "bronze"). `required_skill_level` may be None when not set.

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - achievement_id, name, description, tier, icon,
                - experience_reward, required_level, required_skill_level,
                - required_quest_completions
        """
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "icon": self.icon,
            "experience_reward": self.experience_reward,
            "required_level": self.required_level,
            "required_skill_level": self.required_skill_level,
            "required_quest_completions": self.required_quest_completions,
        }


@dataclass
class UserAchievement:
    """Pure domain entity for user achievements."""

    user_achievement_id: str | None = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    achievement_id: str = ""
    unlocked_at: datetime | None = None
    notes: str = ""

    def __post_init__(self):
        """
        Validate that the instance has a non-empty `achievement_id`.

        Raises:
            ValueError: If `achievement_id` is falsy or an empty string.
        """
        if not self.achievement_id:
            raise ValueError("Achievement ID is required")

    def unlock(self, notes: str = "") -> None:
        """
        Mark the UserAchievement as unlocked.

        Sets `unlocked_at` to the current UTC datetime and stores the provided notes.

        Parameters:
            notes (str): Optional free-form notes to record with the unlock (default: "").
        """
        self.unlocked_at = datetime.utcnow()
        self.notes = notes

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the UserAchievement suitable for serialization.

        The dictionary contains:
        - "user_achievement_id": str | None
        - "user_id": int
        - "achievement_id": str
        - "unlocked_at": ISO 8601 string or None (UTC datetime serialized with datetime.isoformat())
        - "notes": str

        Returns:
            Dict[str, Any]: Mapping of field names to their serializable values.
        """
        return {
            "user_achievement_id": self.user_achievement_id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "notes": self.notes,
        }
