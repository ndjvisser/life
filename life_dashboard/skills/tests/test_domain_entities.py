"""
Fast unit tests for Skills domain entities.

These tests run without Django and focus on pure business logic validation.
"""

from datetime import datetime, timedelta, timezone

import pytest

from life_dashboard.skills.domain.entities import (
    Skill,
    SkillCategory,
    SkillMasteryLevel,
)
from life_dashboard.skills.domain.value_objects import (
    CategoryName,
    ExperienceAmount,
    ExperiencePoints,
    SkillCategoryId,
    SkillId,
    SkillLevel,
    SkillName,
    UserId,
)


class TestSkillCategory:
    """Test SkillCategory domain entity"""

    def test_skill_category_creation_with_valid_data(self):
        """Test creating a skill category with valid data"""
        category = SkillCategory(
            category_id=SkillCategoryId(1),
            name=CategoryName("Programming"),
            description="Software development and programming skills",
            icon="code",
        )

        assert category.category_id.value == 1
        assert category.name.value == "Programming"
        assert category.description == "Software development and programming skills"
        assert category.icon == "code"

    def test_skill_category_description_validation(self):
        """Test skill category description length validation"""
        with pytest.raises(
            ValueError, match="Category description cannot exceed 1000 characters"
        ):
            SkillCategory(
                category_id=SkillCategoryId(1),
                name=CategoryName("Test"),
                description="x" * 1001,  # Too long
            )

    def test_skill_category_icon_validation(self):
        """Test skill category icon length validation"""
        with pytest.raises(
            ValueError, match="Category icon cannot exceed 50 characters"
        ):
            SkillCategory(
                category_id=SkillCategoryId(1),
                name=CategoryName("Test"),
                description="Test category",
                icon="x" * 51,  # Too long
            )


class TestSkill:
    """Test Skill domain entity"""

    def test_skill_creation_with_valid_data(self):
        """Test creating a skill with valid data"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Python Programming"),
            description="Python development skills",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(2500),
            experience_to_next_level=ExperiencePoints(1500),
        )

        assert skill.skill_id.value == 1
        assert skill.name.value == "Python Programming"
        assert skill.level.value == 5
        assert skill.experience_points.value == 2500

    def test_skill_description_validation(self):
        """Test skill description length validation"""
        with pytest.raises(
            ValueError, match="Skill description cannot exceed 1000 characters"
        ):
            Skill(
                skill_id=SkillId(1),
                user_id=UserId(1),
                category_id=SkillCategoryId(1),
                name=SkillName("Test Skill"),
                description="x" * 1001,  # Too long
                level=SkillLevel(1),
                experience_points=ExperiencePoints(0),
                experience_to_next_level=ExperiencePoints(1000),
            )

    def test_skill_mastery_level_calculation(self):
        """Test skill mastery level calculation based on level"""
        # Test Novice (1-20)
        skill_novice = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(15),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert skill_novice.get_mastery_level() == SkillMasteryLevel.NOVICE

        # Test Apprentice (21-40)
        skill_apprentice = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(30),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert skill_apprentice.get_mastery_level() == SkillMasteryLevel.APPRENTICE

        # Test Master (81-100)
        skill_master = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(95),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(
                5000
            ),  # Non-zero for non-max level
        )
        assert skill_master.get_mastery_level() == SkillMasteryLevel.MASTER

    def test_skill_total_experience_calculation(self):
        """Test total experience calculation for target levels"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(1),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )

        # Level 1 should require 0 experience
        assert skill.calculate_total_experience_for_level(1) == 0

        # Level 2 should require 1000 experience
        assert skill.calculate_total_experience_for_level(2) == 1000

        # Level 3 should require 1000 + 1100 = 2100 experience
        assert skill.calculate_total_experience_for_level(3) == 2100

    def test_skill_progress_percentage_calculation(self):
        """Test progress percentage calculation"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(2),
            experience_points=ExperiencePoints(550),  # Halfway to level 3
            experience_to_next_level=ExperiencePoints(550),
        )

        progress = skill.calculate_progress_percentage()
        assert 45.0 <= progress <= 55.0  # Should be around 50%

    def test_skill_can_level_up(self):
        """Test level up eligibility check"""
        # Skill that can level up
        skill_ready = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(1500),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert skill_ready.can_level_up()

        # Skill that cannot level up
        skill_not_ready = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(500),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert not skill_not_ready.can_level_up()

        # Max level skill cannot level up
        skill_max_level = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(100),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(0),
        )
        assert not skill_max_level.can_level_up()

    def test_skill_add_experience_single_level(self):
        """Test adding experience that results in one level up"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(1),
            experience_points=ExperiencePoints(800),
            experience_to_next_level=ExperiencePoints(1000),
        )

        # Add 300 experience (should level up to level 2)
        updated_skill, levels_gained = skill.add_experience(ExperienceAmount(300))

        assert updated_skill.level.value == 2
        assert levels_gained == [2]
        assert updated_skill.experience_points.value == 100  # 800 + 300 - 1000
        assert updated_skill.last_practiced is not None

    def test_skill_add_experience_multiple_levels(self):
        """Test adding experience that results in multiple level ups"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(1),
            experience_points=ExperiencePoints(500),
            experience_to_next_level=ExperiencePoints(1000),
        )

        # Add 2000 experience (should level up multiple times)
        updated_skill, levels_gained = skill.add_experience(ExperienceAmount(2000))

        assert updated_skill.level.value >= 2
        assert len(levels_gained) >= 2
        assert 2 in levels_gained

    def test_skill_add_experience_at_max_level(self):
        """Test adding experience to max level skill"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(100),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(0),
        )

        # Adding experience to max level should not change anything
        updated_skill, levels_gained = skill.add_experience(ExperienceAmount(1000))

        assert updated_skill.level.value == 100
        assert levels_gained == []
        assert updated_skill.experience_points.value == 0

    def test_skill_rank_calculation(self):
        """Test skill rank calculation based on level and mastery"""
        # Test Beginner (Novice, level 1-5)
        skill_beginner = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(3),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert skill_beginner.get_skill_rank() == "Beginner"

        # Test Apprentice (Apprentice, level 21-25)
        skill_apprentice = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(23),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )
        assert skill_apprentice.get_skill_rank() == "Apprentice"

        # Test Supreme Master (Master, level 96-100)
        skill_supreme = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(98),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(
                8000
            ),  # Non-zero for non-max level
        )
        assert skill_supreme.get_skill_rank() == "Supreme Master"

    def test_skill_practice_efficiency_calculation(self):
        """Test practice efficiency based on recency"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )

        # Recent practice (1 day) should have full efficiency
        assert skill.calculate_practice_efficiency(1) == 1.0

        # Moderate gap (7 days) should have reduced efficiency
        assert skill.calculate_practice_efficiency(7) == 0.8

        # Long gap (60 days) should have minimum efficiency
        assert skill.calculate_practice_efficiency(60) == 0.5

    def test_skill_stagnation_detection(self):
        """Test skill stagnation detection"""
        # Skill never practiced
        skill_never_practiced = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
            last_practiced=None,
        )
        assert skill_never_practiced.is_stagnant(30)

        # Skill practiced recently
        skill_recent = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
            last_practiced=datetime.now(timezone.utc) - timedelta(days=10),
        )
        assert not skill_recent.is_stagnant(30)

        # Skill practiced long ago
        skill_stagnant = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(5),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
            last_practiced=datetime.now(timezone.utc) - timedelta(days=45),
        )
        assert skill_stagnant.is_stagnant(30)

    def test_skill_milestone_levels(self):
        """Test milestone level calculation"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(12),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )

        milestones = skill.get_milestone_levels()

        # Should include milestones above current level (12)
        assert 15 in milestones
        assert 20 in milestones
        assert 25 in milestones

        # Should not include milestones at or below current level
        assert 10 not in milestones
        assert 5 not in milestones

    def test_skill_next_milestone(self):
        """Test next milestone calculation"""
        skill = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(12),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(1000),
        )

        next_milestone = skill.next_milestone()
        assert next_milestone == 15  # Next milestone after level 12

        # Max level skill should have no next milestone
        skill_max = Skill(
            skill_id=SkillId(1),
            user_id=UserId(1),
            category_id=SkillCategoryId(1),
            name=SkillName("Test Skill"),
            description="Test",
            level=SkillLevel(100),
            experience_points=ExperiencePoints(0),
            experience_to_next_level=ExperiencePoints(0),
        )

        assert skill_max.next_milestone() is None
