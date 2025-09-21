"""
Skills Domain Services

Pure business logic services for skills operations.
No Django dependencies allowed in this module.
"""

from datetime import datetime, timezone
from typing import Any, cast

from .entities import Skill, SkillCategory, SkillMasteryLevel
from .repositories import SkillCategoryRepository, SkillRepository
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


class SkillService:
    """Service for skill business operations"""

    def __init__(
        self,
        skill_repository: SkillRepository,
        category_repository: SkillCategoryRepository,
    ):
        self._skill_repository = skill_repository
        self._category_repository = category_repository

    def create_skill(
        self,
        user_id: UserId,
        category_id: SkillCategoryId,
        name: str,
        description: str = "",
    ) -> Skill:
        """Create a new skill with validation"""
        # Validate category exists
        category = self._category_repository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category {category_id.value} not found")

        # Create value objects with validation
        skill_name = SkillName(name)

        # Generate skill ID (in real implementation, this would come from repository)
        skill_id = SkillId(1)  # Placeholder

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=skill_name,
            description=description,
            level=SkillLevel(1),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(
                1000
            ),  # Base experience for level 2
        )

        return self._skill_repository.save(skill)

    def add_experience(
        self, skill_id: SkillId, amount: int, practice_notes: str = ""
    ) -> tuple[Skill, list[int]]:
        """Add experience to a skill and return updated skill with levels gained"""
        skill = self._skill_repository.get_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill {skill_id.value} not found")

        # Create experience amount value object with validation
        exp_amount = ExperienceAmount(amount)

        # Add experience and get levels gained
        updated_skill, levels_gained = skill.add_experience(exp_amount)

        # Save updated skill
        saved_skill = self._skill_repository.save(updated_skill)

        return saved_skill, levels_gained

    def practice_skill(
        self,
        skill_id: SkillId,
        practice_duration_minutes: int,
        practice_notes: str = "",
    ) -> tuple[Skill, int, list[int]]:
        """Practice a skill and calculate experience based on duration and efficiency"""
        skill = self._skill_repository.get_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill {skill_id.value} not found")

        # Calculate days since last practice
        days_since_practice = 0
        if skill.last_practiced:
            last_practiced = (
                skill.last_practiced
                if skill.last_practiced.tzinfo is not None
                else skill.last_practiced.replace(tzinfo=timezone.utc)
            )
            days_since_practice = (
                datetime.now(timezone.utc) - last_practiced
            ).days

        # Calculate practice efficiency
        efficiency = skill.calculate_practice_efficiency(days_since_practice)

        # Calculate base experience (10 exp per minute)
        base_experience = practice_duration_minutes * 10

        # Apply efficiency multiplier
        final_experience = int(base_experience * efficiency)

        # Add experience
        updated_skill, levels_gained = self.add_experience(skill_id, final_experience)

        return updated_skill, final_experience, levels_gained

    def get_skill_recommendations(self, user_id: UserId, limit: int = 5) -> list[Skill]:
        """Get skill recommendations based on user's current skills"""
        user_skills = self._skill_repository.get_user_skills(user_id)

        if not user_skills:
            return []

        # Find stagnant skills (not practiced in 30+ days)
        stagnant_skills = [skill for skill in user_skills if skill.is_stagnant(30)]

        # Sort by level (higher level skills first for maintenance)
        stagnant_skills.sort(key=lambda s: s.level.value, reverse=True)

        return stagnant_skills[:limit]

    def calculate_skill_distribution(self, user_id: UserId) -> dict[str, int]:
        """Calculate distribution of skills across mastery levels"""
        user_skills = self._skill_repository.get_user_skills(user_id)

        distribution = {
            SkillMasteryLevel.NOVICE.value: 0,
            SkillMasteryLevel.APPRENTICE.value: 0,
            SkillMasteryLevel.JOURNEYMAN.value: 0,
            SkillMasteryLevel.EXPERT.value: 0,
            SkillMasteryLevel.MASTER.value: 0,
        }

        for skill in user_skills:
            mastery = skill.get_mastery_level()
            distribution[mastery.value] += 1

        return distribution

    def get_skill_progress_summary(
        self, user_id: UserId, *, current_time: datetime | None = None
    ) -> dict[str, Any]:
        """Get comprehensive skill progress summary for a user"""
        user_skills = self._skill_repository.get_user_skills(user_id)

        if not user_skills:
            return {
                "total_skills": 0,
                "average_level": 0.0,
                "total_experience": 0,
                "mastery_distribution": {},
                "top_skills": [],
                "stagnant_skills": [],
                "next_milestones": [],
            }

        # Use provided time for deterministic calculations when needed
        reference_time = current_time or datetime.now(timezone.utc)
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)

        # Calculate statistics
        total_skills = len(user_skills)
        total_experience = sum(
            skill.calculate_total_experience_for_level(skill.level.value)
            + skill.experience_points.value
            for skill in user_skills
        )
        average_level = sum(skill.level.value for skill in user_skills) / total_skills

        # Get mastery distribution
        mastery_distribution = self.calculate_skill_distribution(user_id)

        # Get top skills
        top_skills = sorted(user_skills, key=lambda s: s.level.value, reverse=True)[:5]

        # Get stagnant skills
        stagnant_skills = [
            skill
            for skill in user_skills
            if skill.is_stagnant(30, current_time=reference_time)
        ]

        # Get next milestones
        next_milestones = []
        for skill in user_skills:
            milestone = skill.next_milestone()
            if milestone:
                next_milestones.append(
                    {
                        "skill_name": skill.name.value,
                        "current_level": skill.level.value,
                        "next_milestone": milestone,
                        "progress_percentage": skill.calculate_progress_percentage(),
                    }
                )

        # Sort milestones by progress (closest first)
        next_milestones.sort(
            key=lambda m: cast(float, m.get("progress_percentage", 0.0)),
            reverse=True,
        )

        return {
            "total_skills": total_skills,
            "average_level": round(average_level, 2),
            "total_experience": total_experience,
            "mastery_distribution": mastery_distribution,
            "top_skills": [
                {
                    "name": skill.name.value,
                    "level": skill.level.value,
                    "mastery": skill.get_mastery_level().value,
                    "rank": skill.get_skill_rank(),
                }
                for skill in top_skills
            ],
            "stagnant_skills": [
                {
                    "name": skill.name.value,
                    "level": skill.level.value,
                    "days_since_practice": (
                        reference_time
                        - (
                            skill.last_practiced
                            if skill.last_practiced.tzinfo is not None
                            else skill.last_practiced.replace(tzinfo=timezone.utc)
                        )
                    ).days
                    if skill.last_practiced
                    else None,
                }
                for skill in stagnant_skills[:5]
            ],
            "next_milestones": next_milestones[:10],
        }


class SkillCategoryService:
    """Service for skill category business operations"""

    def __init__(self, category_repository: SkillCategoryRepository):
        self._category_repository = category_repository

    def create_category(
        self,
        name: str,
        description: str = "",
        icon: str = "",
    ) -> SkillCategory:
        """Create a new skill category with validation"""
        # Create value objects with validation
        category_name = CategoryName(name)

        # Generate category ID (in real implementation, this would come from repository)
        category_id = SkillCategoryId(1)  # Placeholder

        category = SkillCategory(
            category_id=category_id,
            name=category_name,
            description=description,
            icon=icon,
        )

        return self._category_repository.save(category)

    def get_category_statistics(
        self, category_id: SkillCategoryId, user_id: UserId
    ) -> dict[str, Any]:
        """Get statistics for a specific category for a user"""
        # This would typically involve cross-repository queries
        # For now, return a placeholder structure
        return {
            "category_id": category_id.value,
            "total_skills": 0,
            "average_level": 0.0,
            "highest_level_skill": None,
            "total_practice_time": 0,
        }
