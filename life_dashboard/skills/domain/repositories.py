"""
Skills Domain Repositories

Abstract repository interfaces for skills data access.
No Django dependencies allowed in this module.
"""

from abc import ABC, abstractmethod

from .entities import Skill, SkillCategory
from .value_objects import SkillCategoryId, SkillId, UserId


class SkillRepository(ABC):
    """Abstract repository for skill data access"""

    @abstractmethod
    def save(self, skill: Skill) -> Skill:
        """Save a skill entity"""
        pass

    @abstractmethod
    def get_by_id(self, skill_id: SkillId) -> Skill | None:
        """Get skill by ID"""
        pass

    @abstractmethod
    def get_user_skills(self, user_id: UserId) -> list[Skill]:
        """Get all skills for a user"""
        pass

    @abstractmethod
    def get_skills_by_category(
        self, user_id: UserId, category_id: SkillCategoryId
    ) -> list[Skill]:
        """Get skills for a user in a specific category"""
        pass

    @abstractmethod
    def get_skills_by_mastery_level(
        self, user_id: UserId, mastery_level: str
    ) -> list[Skill]:
        """Get skills for a user at a specific mastery level"""
        pass

    @abstractmethod
    def get_top_skills(self, user_id: UserId, limit: int = 10) -> list[Skill]:
        """Get top skills for a user by level"""
        pass

    @abstractmethod
    def delete(self, skill_id: SkillId) -> bool:
        """Delete a skill"""
        pass


class SkillCategoryRepository(ABC):
    """Abstract repository for skill category data access"""

    @abstractmethod
    def save(self, category: SkillCategory) -> SkillCategory:
        """Save a skill category entity"""
        pass

    @abstractmethod
    def get_by_id(self, category_id: SkillCategoryId) -> SkillCategory | None:
        """Get skill category by ID"""
        pass

    @abstractmethod
    def get_all_categories(self) -> list[SkillCategory]:
        """Get all skill categories"""
        pass

    @abstractmethod
    def get_categories_with_skills(self, user_id: UserId) -> list[SkillCategory]:
        """Get categories that have skills for a specific user"""
        pass

    @abstractmethod
    def delete(self, category_id: SkillCategoryId) -> bool:
        """Delete a skill category"""
        pass
