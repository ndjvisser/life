"""
Property-based tests for Skills domain using Hypothesis.

These tests generate random inputs to validate domain invariants and edge cases.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import composite

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


# Custom strategies for domain objects
@composite
def skill_ids(draw):
    """Generate valid skill IDs"""
    return SkillId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def category_ids(draw):
    """Generate valid category IDs"""
    return SkillCategoryId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def user_ids(draw):
    """Generate valid user IDs"""
    return UserId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def skill_names(draw):
    """Generate valid skill names"""
    name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    return SkillName(name)


@composite
def category_names(draw):
    """Generate valid category names"""
    name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    return CategoryName(name)


@composite
def skill_levels(draw):
    """Generate valid skill levels"""
    return SkillLevel(draw(st.integers(min_value=1, max_value=100)))


@composite
def experience_points(draw):
    """Generate valid experience points"""
    return ExperiencePoints(draw(st.integers(min_value=0, max_value=2**31 - 1)))


@composite
def experience_amounts(draw):
    """Generate valid experience amounts"""
    return ExperienceAmount(draw(st.integers(min_value=1, max_value=1000000)))


class TestSkillCategoryProperties:
    """Property-based tests for SkillCategory entity"""

    @given(
        category_id=category_ids(),
        name=category_names(),
        description=st.text(max_size=1000),
        icon=st.text(max_size=50),
    )
    def test_skill_category_creation_always_valid_with_valid_inputs(
        self, category_id, name, description, icon
    ):
        """Test that skill category creation always succeeds with valid inputs"""
        category = SkillCategory(
            category_id=category_id,
            name=name,
            description=description,
            icon=icon,
        )

        assert category.category_id == category_id
        assert category.name == name
        assert category.description == description
        assert category.icon == icon

    @given(st.text(min_size=1001))
    def test_skill_category_rejects_long_descriptions(self, description):
        """Test that skill categories reject descriptions over 1000 characters"""
        with pytest.raises(ValueError):
            SkillCategory(
                category_id=SkillCategoryId(1),
                name=CategoryName("Test"),
                description=description,
            )

    @given(st.text(min_size=51))
    def test_skill_category_rejects_long_icons(self, icon):
        """Test that skill categories reject icons over 50 characters"""
        with pytest.raises(ValueError):
            SkillCategory(
                category_id=SkillCategoryId(1),
                name=CategoryName("Test"),
                description="Test",
                icon=icon,
            )


class TestSkillProperties:
    """Property-based tests for Skill entity"""

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        description=st.text(max_size=1000),
        level=skill_levels(),
        experience_points=experience_points(),
    )
    def test_skill_creation_always_valid_with_valid_inputs(
        self,
        skill_id,
        user_id,
        category_id,
        name,
        description,
        level,
        experience_points,
    ):
        """Test that skill creation always succeeds with valid inputs"""
        # Calculate appropriate experience_to_next_level
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description=description,
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        assert skill.skill_id == skill_id
        assert skill.user_id == user_id
        assert skill.name == name
        assert skill.level == level

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
    )
    def test_skill_mastery_level_is_deterministic(
        self, skill_id, user_id, category_id, name, level, experience_points
    ):
        """Test that mastery level calculation is deterministic"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        mastery = skill.get_mastery_level()

        # Verify mastery level matches expected ranges
        if level.value <= 20:
            assert mastery == SkillMasteryLevel.NOVICE
        elif level.value <= 40:
            assert mastery == SkillMasteryLevel.APPRENTICE
        elif level.value <= 60:
            assert mastery == SkillMasteryLevel.JOURNEYMAN
        elif level.value <= 80:
            assert mastery == SkillMasteryLevel.EXPERT
        else:
            assert mastery == SkillMasteryLevel.MASTER

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
        target_level=st.integers(min_value=1, max_value=100),
    )
    def test_total_experience_calculation_is_monotonic(
        self,
        skill_id,
        user_id,
        category_id,
        name,
        level,
        experience_points,
        target_level,
    ):
        """Test that total experience calculation is monotonically increasing"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        # Test that higher levels require more total experience
        if target_level > 1:
            exp_current = skill.calculate_total_experience_for_level(target_level)
            exp_previous = skill.calculate_total_experience_for_level(target_level - 1)
            assert exp_current >= exp_previous

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
    )
    def test_progress_percentage_is_bounded(
        self, skill_id, user_id, category_id, name, level, experience_points
    ):
        """Test that progress percentage is always between 0 and 100"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        progress = skill.calculate_progress_percentage()
        assert 0.0 <= progress <= 100.0

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=st.integers(min_value=1, max_value=99).map(SkillLevel),  # Not max level
        experience_points=experience_points(),
        exp_amount=experience_amounts(),
    )
    def test_add_experience_never_decreases_level(
        self, skill_id, user_id, category_id, name, level, experience_points, exp_amount
    ):
        """Test that adding experience never decreases skill level"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        original_level = skill.level.value
        updated_skill, levels_gained = skill.add_experience(exp_amount)

        # Level should never decrease
        assert updated_skill.level.value >= original_level

        # Levels gained should be non-negative
        assert len(levels_gained) >= 0

        # All levels gained should be greater than original level
        for gained_level in levels_gained:
            assert gained_level > original_level

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
        days_since_practice=st.integers(min_value=0, max_value=365),
    )
    def test_practice_efficiency_is_bounded_and_decreasing(
        self,
        skill_id,
        user_id,
        category_id,
        name,
        level,
        experience_points,
        days_since_practice,
    ):
        """Test that practice efficiency is bounded and decreases over time"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        efficiency = skill.calculate_practice_efficiency(days_since_practice)

        # Efficiency should be between 0.5 and 1.0
        assert 0.5 <= efficiency <= 1.0

        # Recent practice should have higher efficiency than old practice
        if days_since_practice <= 1:
            assert efficiency == 1.0
        elif days_since_practice > 30:
            assert efficiency == 0.5

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
    )
    def test_skill_rank_is_consistent_with_mastery(
        self, skill_id, user_id, category_id, name, level, experience_points
    ):
        """Test that skill rank is consistent with mastery level"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        mastery = skill.get_mastery_level()
        rank = skill.get_skill_rank()

        # Verify rank contains expected keywords based on mastery
        if mastery == SkillMasteryLevel.NOVICE:
            assert any(
                word in rank
                for word in ["Beginner", "Learning", "Developing", "Improving"]
            )
        elif mastery == SkillMasteryLevel.APPRENTICE:
            assert "Apprentice" in rank
        elif mastery == SkillMasteryLevel.JOURNEYMAN:
            assert "Journeyman" in rank
        elif mastery == SkillMasteryLevel.EXPERT:
            assert "Expert" in rank
        elif mastery == SkillMasteryLevel.MASTER:
            assert "Master" in rank

    @given(
        skill_id=skill_ids(),
        user_id=user_ids(),
        category_id=category_ids(),
        name=skill_names(),
        level=skill_levels(),
        experience_points=experience_points(),
    )
    def test_milestone_levels_are_sorted_and_above_current_level(
        self, skill_id, user_id, category_id, name, level, experience_points
    ):
        """Test that milestone levels are sorted and above current level"""
        exp_to_next = ExperiencePoints(max(1, int(1000 * (1.1 ** (level.value - 1)))))

        skill = Skill(
            skill_id=skill_id,
            user_id=user_id,
            category_id=category_id,
            name=name,
            description="Test",
            level=level,
            experience_points=experience_points,
            experience_to_next_level=exp_to_next,
        )

        milestones = skill.get_milestone_levels()

        # All milestones should be above current level
        for milestone in milestones:
            assert milestone > level.value

        # Milestones should be sorted in ascending order
        assert milestones == sorted(milestones)

        # Next milestone should be the first in the list (if any)
        next_milestone = skill.next_milestone()
        if milestones:
            assert next_milestone == milestones[0]
        else:
            assert next_milestone is None


class TestValueObjectProperties:
    """Property-based tests for value objects"""

    @given(st.integers(min_value=1, max_value=1000000))
    def test_skill_id_always_positive(self, value):
        """Test that SkillId always accepts positive values"""
        skill_id = SkillId(value)
        assert skill_id.value == value
        assert skill_id.value > 0

    @given(st.integers(max_value=0))
    def test_skill_id_rejects_non_positive(self, value):
        """Test that SkillId rejects non-positive values"""
        with pytest.raises(ValueError):
            SkillId(value)

    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_skill_name_accepts_valid_strings(self, name):
        """Test that SkillName accepts valid strings"""
        skill_name = SkillName(name)
        assert skill_name.value == name

    @given(st.text(min_size=101))
    def test_skill_name_rejects_long_strings(self, name):
        """Test that SkillName rejects strings over 100 characters"""
        with pytest.raises(ValueError):
            SkillName(name)

    @given(st.integers(min_value=1, max_value=100))
    def test_skill_level_accepts_valid_range(self, value):
        """Test that SkillLevel accepts valid range"""
        level = SkillLevel(value)
        assert level.value == value
        assert 1 <= level.value <= 100

    @given(st.integers(max_value=0))
    def test_skill_level_rejects_zero_or_negative(self, value):
        """Test that SkillLevel rejects zero or negative values"""
        with pytest.raises(ValueError):
            SkillLevel(value)

    @given(st.integers(min_value=101))
    def test_skill_level_rejects_excessive_values(self, value):
        """Test that SkillLevel rejects values over 100"""
        with pytest.raises(ValueError):
            SkillLevel(value)

    @given(st.integers(min_value=0, max_value=2**31 - 1))
    def test_experience_points_accepts_valid_range(self, value):
        """Test that ExperiencePoints accepts valid range"""
        exp = ExperiencePoints(value)
        assert exp.value == value
        assert 0 <= exp.value <= 2**31 - 1

    @given(st.integers(max_value=-1))
    def test_experience_points_rejects_negative(self, value):
        """Test that ExperiencePoints rejects negative values"""
        with pytest.raises(ValueError):
            ExperiencePoints(value)

    @given(st.integers(min_value=1, max_value=1000000))
    def test_experience_amount_accepts_valid_range(self, value):
        """Test that ExperienceAmount accepts valid range"""
        amount = ExperienceAmount(value)
        assert amount.value == value
        assert 1 <= amount.value <= 1000000

    @given(st.integers(max_value=0))
    def test_experience_amount_rejects_non_positive(self, value):
        """Test that ExperienceAmount rejects non-positive values"""
        with pytest.raises(ValueError):
            ExperienceAmount(value)
