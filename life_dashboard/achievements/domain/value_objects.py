"""
Achievements Domain Value Objects

Immutable value objects that encapsulate domain constraints and validation.
No Django dependencies allowed in this module.
"""
from dataclasses import dataclass

from life_dashboard.common.value_objects import ExperienceReward, UserId


@dataclass(frozen=True)
class AchievementId:
    """Achievement identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Achievement ID must be positive")


@dataclass(frozen=True)
class UserAchievementId:
    """User achievement identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("User achievement ID must be positive")


@dataclass(frozen=True)
class AchievementName:
    """Achievement name value object with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Achievement name cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Achievement name cannot exceed 200 characters")


@dataclass(frozen=True)
class AchievementDescription:
    """Achievement description value object"""

    value: str

    def __post_init__(self):
        if len(self.value) > 2000:
            raise ValueError("Achievement description cannot exceed 2000 characters")


@dataclass(frozen=True)
class RequiredLevel:
    """Required level value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 1:
            raise ValueError("Required level must be at least 1")
        if self.value > 100:
            raise ValueError("Required level cannot exceed 100")


@dataclass(frozen=True)
class RequiredSkillLevel:
    """Required skill level value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 1:
            raise ValueError("Required skill level must be at least 1")
        if self.value > 100:
            raise ValueError("Required skill level cannot exceed 100")


@dataclass(frozen=True)
class RequiredQuestCompletions:
    """Required quest completions value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Required quest completions cannot be negative")
        if self.value > 10000:  # Reasonable upper limit
            raise ValueError("Required quest completions cannot exceed 10000")


@dataclass(frozen=True)
class AchievementIcon:
    """Achievement icon value object with validation"""

    value: str

    def __post_init__(self):
        if len(self.value) > 50:
            raise ValueError("Achievement icon cannot exceed 50 characters")
