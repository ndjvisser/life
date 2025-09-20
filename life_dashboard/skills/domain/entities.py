"""
Skills Domain Entities

Pure Python domain objects representing core skills business concepts.
No Django dependencies allowed in this module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .value_objects import (
    CategoryName,
    ExperienceAmount,
    ExperiencePoints,
    SkillCategoryId,
    SkillId,
    SkillLevel,
    SkillName,
    UserId,
)


class SkillMasteryLevel(Enum):
    """Skill mastery level enumeration"""

    NOVICE = "novice"  # Levels 1-20
    APPRENTICE = "apprentice"  # Levels 21-40
    JOURNEYMAN = "journeyman"  # Levels 41-60
    EXPERT = "expert"  # Levels 61-80
    MASTER = "master"  # Levels 81-100


@dataclass
class SkillCategory:
    """
    Skill category domain entity representing a grouping of related skills.

    Contains pure business logic for skill categorization and organization.
    """

    category_id: SkillCategoryId
    name: CategoryName
    description: str
    icon: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate category data after initialization"""
        if len(self.description) > 1000:
            raise ValueError("Category description cannot exceed 1000 characters")
        if len(self.icon) > 50:
            raise ValueError("Category icon cannot exceed 50 characters")


@dataclass
class Skill:
    """
    Skill domain entity representing a user's skill with progression tracking.

    Contains pure business logic for skill progression, experience calculation,
    and mastery level determination.
    """

    skill_id: SkillId
    user_id: UserId
    category_id: SkillCategoryId
    name: SkillName
    description: str
    level: SkillLevel
    experience_points: ExperiencePoints
    experience_to_next_level: ExperiencePoints
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_practiced: datetime | None = None

    def __post_init__(self):
        """Validate skill data after initialization"""
        if len(self.description) > 1000:
            raise ValueError("Skill description cannot exceed 1000 characters")

        # Validate experience consistency
        if self.level.value == 100 and self.experience_points.value > 0:
            # At max level, experience should be 0
            pass  # Allow for flexibility in max level handling

        if self.level.value < 100 and self.experience_to_next_level.value <= 0:
            raise ValueError(
                "Experience to next level must be positive for non-max level skills"
            )

    def get_mastery_level(self) -> SkillMasteryLevel:
        """Get the mastery level based on current skill level"""
        level = self.level.value
        if level <= 20:
            return SkillMasteryLevel.NOVICE
        elif level <= 40:
            return SkillMasteryLevel.APPRENTICE
        elif level <= 60:
            return SkillMasteryLevel.JOURNEYMAN
        elif level <= 80:
            return SkillMasteryLevel.EXPERT
        else:
            return SkillMasteryLevel.MASTER

    def calculate_total_experience_for_level(self, target_level: int) -> int:
        """Calculate total experience needed to reach a target level"""
        if target_level < 1 or target_level > 100:
            raise ValueError("Target level must be between 1 and 100")

        if target_level == 1:
            return 0

        # Calculate cumulative experience needed
        total_exp = 0
        exp_for_level = 1000  # Base experience for level 2

        for _level in range(2, target_level + 1):
            total_exp += exp_for_level
            exp_for_level = min(int(exp_for_level * 1.1), 2**31 - 1)

        return total_exp

    def calculate_progress_percentage(self) -> float:
        """Calculate progress percentage to next level"""
        if self.level.value >= 100:
            return 100.0

        current_level_exp = self.calculate_total_experience_for_level(self.level.value)
        next_level_exp = self.calculate_total_experience_for_level(self.level.value + 1)
        total_exp = current_level_exp + self.experience_points.value

        if next_level_exp == current_level_exp:
            return 100.0

        progress = (total_exp - current_level_exp) / (
            next_level_exp - current_level_exp
        )
        return min(max(progress * 100, 0.0), 100.0)

    def can_level_up(self) -> bool:
        """Check if skill has enough experience to level up"""
        return (
            self.level.value < 100
            and self.experience_points.value >= self.experience_to_next_level.value
        )

    def add_experience(self, amount: ExperienceAmount) -> tuple["Skill", list[int]]:
        """
        Add experience to the skill and return updated skill with levels gained.

        Returns:
            Tuple of (updated_skill, levels_gained_list)
        """
        if self.level.value >= 100:
            # Max level reached, no more experience can be added
            return self, []

        # Calculate new experience total
        new_total_exp = min(
            self.experience_points.value + amount.value,
            2**31 - 1,  # Cap at max value
        )

        current_level = self.level.value
        current_exp = new_total_exp
        exp_to_next = self.experience_to_next_level.value
        levels_gained = []

        # Process level ups
        while current_level < 100 and current_exp >= exp_to_next:
            current_exp -= exp_to_next
            current_level += 1
            levels_gained.append(current_level)

            # Calculate experience needed for next level (10% increase)
            exp_to_next = min(int(exp_to_next * 1.1), 2**31 - 1)

        # Create updated skill
        updated_skill = Skill(
            skill_id=self.skill_id,
            user_id=self.user_id,
            category_id=self.category_id,
            name=self.name,
            description=self.description,
            level=SkillLevel(current_level),
            experience_points=ExperiencePoints(current_exp),
            experience_to_next_level=ExperiencePoints(
                exp_to_next if current_level < 100 else 0
            ),
            created_at=self.created_at,
            last_practiced=datetime.utcnow(),
        )

        return updated_skill, levels_gained

    def get_skill_rank(self) -> str:
        """Get a descriptive rank based on level and mastery"""
        mastery = self.get_mastery_level()
        level = self.level.value

        if mastery == SkillMasteryLevel.NOVICE:
            if level <= 5:
                return "Beginner"
            elif level <= 10:
                return "Learning"
            elif level <= 15:
                return "Developing"
            else:
                return "Improving"
        elif mastery == SkillMasteryLevel.APPRENTICE:
            if level <= 25:
                return "Apprentice"
            elif level <= 30:
                return "Skilled Apprentice"
            elif level <= 35:
                return "Advanced Apprentice"
            else:
                return "Senior Apprentice"
        elif mastery == SkillMasteryLevel.JOURNEYMAN:
            if level <= 45:
                return "Journeyman"
            elif level <= 50:
                return "Skilled Journeyman"
            elif level <= 55:
                return "Advanced Journeyman"
            else:
                return "Senior Journeyman"
        elif mastery == SkillMasteryLevel.EXPERT:
            if level <= 65:
                return "Expert"
            elif level <= 70:
                return "Senior Expert"
            elif level <= 75:
                return "Advanced Expert"
            else:
                return "Master Expert"
        else:  # MASTER
            if level <= 85:
                return "Master"
            elif level <= 90:
                return "Grand Master"
            elif level <= 95:
                return "Legendary Master"
            else:
                return "Supreme Master"

    def calculate_practice_efficiency(self, days_since_last_practice: int) -> float:
        """Calculate practice efficiency based on recency"""
        if days_since_last_practice <= 1:
            return 1.0  # Full efficiency
        elif days_since_last_practice <= 3:
            return 0.9  # Slight decay
        elif days_since_last_practice <= 7:
            return 0.8  # Moderate decay
        elif days_since_last_practice <= 14:
            return 0.7  # Significant decay
        elif days_since_last_practice <= 30:
            return 0.6  # Major decay
        else:
            return 0.5  # Minimum efficiency

    def is_stagnant(self, days_threshold: int = 30) -> bool:
        """Check if skill has been stagnant (not practiced recently)"""
        if not self.last_practiced:
            return True

        days_since_practice = (datetime.utcnow() - self.last_practiced).days
        return days_since_practice > days_threshold

    def get_milestone_levels(self) -> list[int]:
        """Get list of milestone levels for this skill"""
        milestones = [5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
        return [level for level in milestones if level > self.level.value]

    def next_milestone(self) -> int | None:
        """Get the next milestone level"""
        milestones = self.get_milestone_levels()
        return milestones[0] if milestones else None
