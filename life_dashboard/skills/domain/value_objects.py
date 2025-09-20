"""
Skills Domain Value Objects

Immutable value objects that encapsulate domain constraints and validation.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillId:
    """Skill identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Skill ID must be positive")


@dataclass(frozen=True)
class SkillCategoryId:
    """Skill category identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Skill category ID must be positive")


@dataclass(frozen=True)
class UserId:
    """User identifier value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("User ID must be positive")


@dataclass(frozen=True)
class SkillName:
    """Skill name value object with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Skill name cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Skill name cannot exceed 100 characters")


@dataclass(frozen=True)
class CategoryName:
    """Category name value object with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Category name cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Category name cannot exceed 100 characters")


@dataclass(frozen=True)
class SkillLevel:
    """Skill level value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 1:
            raise ValueError("Skill level must be at least 1")
        if self.value > 100:
            raise ValueError("Skill level cannot exceed 100")


@dataclass(frozen=True)
class ExperiencePoints:
    """Experience points value object with validation"""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Experience points cannot be negative")
        if self.value > 2**31 - 1:  # Max 32-bit integer
            raise ValueError("Experience points cannot exceed maximum value")


@dataclass(frozen=True)
class ExperienceAmount:
    """Experience amount value object for adding experience"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Experience amount must be positive")
        if self.value > 1000000:  # Reasonable upper limit for single addition
            raise ValueError(
                "Experience amount cannot exceed 1,000,000 in single addition"
            )
