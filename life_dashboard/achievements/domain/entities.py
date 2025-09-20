"""
Achievements domain entities - pure Python business logic without Django dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
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

    achievement_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    tier: AchievementTier = AchievementTier.BRONZE
    icon: str = ""
    experience_reward: int = 0

    # Requirements
    required_level: int = 1
    required_skill_level: Optional[int] = None
    required_quest_completions: int = 0

    def __post_init__(self):
        if not self.name:
            raise ValueError("Achievement name is required")

        if self.experience_reward < 0:
            raise ValueError("Experience reward cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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

    user_achievement_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    user_id: int = 0
    achievement_id: str = ""
    unlocked_at: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self):
        if not self.achievement_id:
            raise ValueError("Achievement ID is required")

    def unlock(self, notes: str = "") -> None:
        """Unlock the achievement."""
        self.unlocked_at = datetime.utcnow()
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "user_achievement_id": self.user_achievement_id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "notes": self.notes,
        }
