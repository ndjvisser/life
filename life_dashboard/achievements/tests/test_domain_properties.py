"""
Property-based tests for Achievements domain using Hypothesis.

These tests generate random inputs to validate domain invariants and edge cases.
"""

from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("hypothesis")
from hypothesis import assume, given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from life_dashboard.achievements.domain.entities import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
from life_dashboard.achievements.domain.value_objects import (
    AchievementDescription,
    AchievementIcon,
    AchievementId,
    AchievementName,
    ExperienceReward,
    RequiredLevel,
    RequiredQuestCompletions,
    RequiredSkillLevel,
    UserAchievementId,
    UserId,
)


# Custom strategies for domain objects
@composite
def achievement_ids(draw):
    """Generate valid achievement IDs"""
    return AchievementId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def user_achievement_ids(draw):
    """Generate valid user achievement IDs"""
    return UserAchievementId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def user_ids(draw):
    """Generate valid user IDs"""
    return UserId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def achievement_names(draw):
    """Generate valid achievement names"""
    name = draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    return AchievementName(name)


@composite
def achievement_descriptions(draw):
    """Generate valid achievement descriptions"""
    description = draw(st.text(max_size=2000))
    return AchievementDescription(description)


@composite
def experience_rewards(draw):
    """Generate valid experience rewards"""
    return ExperienceReward(
        draw(st.integers(min_value=0, max_value=50000)), max_value=50000
    )


@composite
def required_levels(draw):
    """Generate valid required levels"""
    return RequiredLevel(draw(st.integers(min_value=1, max_value=100)))


@composite
def required_skill_levels(draw):
    """Generate valid required skill levels"""
    return RequiredSkillLevel(draw(st.integers(min_value=1, max_value=100)))


@composite
def required_quest_completions(draw):
    """Generate valid required quest completions"""
    return RequiredQuestCompletions(draw(st.integers(min_value=0, max_value=10000)))


@composite
def achievement_icons(draw):
    """Generate valid achievement icons"""
    icon = draw(st.text(max_size=50))
    return AchievementIcon(icon)


class TestAchievementProperties:
    """Property-based tests for Achievement entity"""

    @given(
        achievement_id=achievement_ids(),
        name=achievement_names(),
        description=achievement_descriptions(),
        tier=st.sampled_from(AchievementTier),
        category=st.sampled_from(AchievementCategory),
        icon=achievement_icons(),
        experience_reward=experience_rewards(),
        required_level=required_levels(),
        required_quest_completions=required_quest_completions(),
    )
    def test_achievement_creation_always_valid_with_valid_inputs(
        self,
        achievement_id,
        name,
        description,
        tier,
        category,
        icon,
        experience_reward,
        required_level,
        required_quest_completions,
    ):
        """Test that achievement creation always succeeds with valid inputs"""
        # Ensure at least one meaningful requirement
        assume(required_level.value > 1 or required_quest_completions.value > 0)

        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            tier=tier,
            category=category,
            icon=icon,
            experience_reward=experience_reward,
            required_level=required_level,
            required_quest_completions=required_quest_completions,
        )

        assert achievement.achievement_id == achievement_id
        assert achievement.name == name
        assert achievement.tier == tier
        assert achievement.category == category

    @given(
        achievement_id=achievement_ids(),
        name=achievement_names(),
        description=achievement_descriptions(),
        tier=st.sampled_from(AchievementTier),
        category=st.sampled_from(AchievementCategory),
        icon=achievement_icons(),
        experience_reward=experience_rewards(),
        required_level=required_levels(),
        required_quest_completions=required_quest_completions(),
    )
    def test_achievement_tier_multiplier_is_consistent(
        self,
        achievement_id,
        name,
        description,
        tier,
        category,
        icon,
        experience_reward,
        required_level,
        required_quest_completions,
    ):
        """Test that tier multipliers are consistent and positive"""
        # Ensure at least one meaningful requirement
        assume(required_level.value > 1 or required_quest_completions.value > 0)

        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            tier=tier,
            category=category,
            icon=icon,
            experience_reward=experience_reward,
            required_level=required_level,
            required_quest_completions=required_quest_completions,
        )

        multiplier = achievement.get_tier_multiplier()
        final_experience = achievement.calculate_final_experience_reward()

        # Multiplier should be positive
        assert multiplier > 0

        # Final experience should be base * multiplier
        expected_experience = int(experience_reward.value * multiplier)
        assert final_experience == expected_experience

        # Verify tier-specific multipliers
        expected_multipliers = {
            AchievementTier.BRONZE: 1.0,
            AchievementTier.SILVER: 1.5,
            AchievementTier.GOLD: 2.0,
            AchievementTier.PLATINUM: 3.0,
        }
        assert multiplier == expected_multipliers[tier]

    @given(
        achievement_id=achievement_ids(),
        name=achievement_names(),
        description=achievement_descriptions(),
        tier=st.sampled_from(AchievementTier),
        category=st.sampled_from(AchievementCategory),
        icon=achievement_icons(),
        experience_reward=experience_rewards(),
        required_level=required_levels(),
        required_skill_level=st.one_of(st.none(), required_skill_levels()),
        required_quest_completions=required_quest_completions(),
        user_level=st.integers(min_value=1, max_value=100),
        max_skill_level=st.integers(min_value=1, max_value=100),
        quest_completions=st.integers(min_value=0, max_value=10000),
    )
    def test_achievement_progress_percentage_is_bounded(
        self,
        achievement_id,
        name,
        description,
        tier,
        category,
        icon,
        experience_reward,
        required_level,
        required_skill_level,
        required_quest_completions,
        user_level,
        max_skill_level,
        quest_completions,
    ):
        """Test that progress percentage is always between 0 and 100"""
        # Ensure at least one meaningful requirement
        assume(
            required_level.value > 1
            or (required_skill_level and required_skill_level.value > 1)
            or required_quest_completions.value > 0
        )

        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            tier=tier,
            category=category,
            icon=icon,
            experience_reward=experience_reward,
            required_level=required_level,
            required_skill_level=required_skill_level,
            required_quest_completions=required_quest_completions,
        )

        user_stats = {
            "level": user_level,
            "max_skill_level": max_skill_level,
            "quest_completions": quest_completions,
        }

        progress = achievement.get_progress_percentage(user_stats)
        assert 0.0 <= progress <= 100.0

    @given(
        achievement_id=achievement_ids(),
        name=achievement_names(),
        description=achievement_descriptions(),
        tier=st.sampled_from(AchievementTier),
        category=st.sampled_from(AchievementCategory),
        icon=achievement_icons(),
        experience_reward=experience_rewards(),
        required_level=required_levels(),
        required_skill_level=st.one_of(st.none(), required_skill_levels()),
        required_quest_completions=required_quest_completions(),
    )
    def test_achievement_eligibility_is_deterministic(
        self,
        achievement_id,
        name,
        description,
        tier,
        category,
        icon,
        experience_reward,
        required_level,
        required_skill_level,
        required_quest_completions,
    ):
        """Test that eligibility checking is deterministic"""
        # Ensure at least one meaningful requirement
        assume(
            required_level.value > 1
            or (required_skill_level and required_skill_level.value > 1)
            or required_quest_completions.value > 0
        )

        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            tier=tier,
            category=category,
            icon=icon,
            experience_reward=experience_reward,
            required_level=required_level,
            required_skill_level=required_skill_level,
            required_quest_completions=required_quest_completions,
        )

        # User that meets all requirements
        exceeding_stats = {
            "level": required_level.value + 10,
            "max_skill_level": (required_skill_level.value + 10)
            if required_skill_level
            else 100,
            "quest_completions": required_quest_completions.value + 10,
        }

        # User that meets no requirements
        insufficient_stats = {
            "level": 1,
            "max_skill_level": 1,
            "quest_completions": 0,
        }

        # User exceeding requirements should be eligible
        assert achievement.check_eligibility(exceeding_stats)

        # User with insufficient stats should not be eligible (unless all requirements are minimal)
        if (
            required_level.value > 1
            or (required_skill_level and required_skill_level.value > 1)
            or required_quest_completions.value > 0
        ):
            assert not achievement.check_eligibility(insufficient_stats)

    @given(
        achievement_id=achievement_ids(),
        name=achievement_names(),
        description=achievement_descriptions(),
        tier=st.sampled_from(AchievementTier),
        category=st.sampled_from(AchievementCategory),
        icon=achievement_icons(),
        experience_reward=experience_rewards(),
        required_level=required_levels(),
        required_skill_level=st.one_of(st.none(), required_skill_levels()),
        required_quest_completions=required_quest_completions(),
    )
    def test_achievement_difficulty_rating_is_consistent(
        self,
        achievement_id,
        name,
        description,
        tier,
        category,
        icon,
        experience_reward,
        required_level,
        required_skill_level,
        required_quest_completions,
    ):
        """Test that difficulty rating is consistent with requirements"""
        # Ensure at least one meaningful requirement
        assume(
            required_level.value > 1
            or (required_skill_level and required_skill_level.value > 1)
            or required_quest_completions.value > 0
        )

        achievement = Achievement(
            achievement_id=achievement_id,
            name=name,
            description=description,
            tier=tier,
            category=category,
            icon=icon,
            experience_reward=experience_reward,
            required_level=required_level,
            required_skill_level=required_skill_level,
            required_quest_completions=required_quest_completions,
        )

        difficulty = achievement.get_difficulty_rating()
        valid_difficulties = ["Easy", "Medium", "Hard", "Very Hard", "Legendary"]
        assert difficulty in valid_difficulties

        # Higher tier achievements should generally be harder
        if tier == AchievementTier.PLATINUM:
            assert difficulty in ["Medium", "Hard", "Very Hard", "Legendary"]


class TestUserAchievementProperties:
    """Property-based tests for UserAchievement entity"""

    @given(
        user_achievement_id=user_achievement_ids(),
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        notes=st.text(max_size=1000),
        days_ago=st.integers(min_value=0, max_value=365),
    )
    def test_user_achievement_creation_always_valid_with_valid_inputs(
        self, user_achievement_id, user_id, achievement_id, notes, days_ago
    ):
        """Test that user achievement creation always succeeds with valid inputs"""
        unlocked_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        user_achievement = UserAchievement(
            user_achievement_id=user_achievement_id,
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=unlocked_at,
            notes=notes,
        )

        assert user_achievement.user_achievement_id == user_achievement_id
        assert user_achievement.user_id == user_id
        assert user_achievement.achievement_id == achievement_id
        assert user_achievement.notes == notes

    @given(
        user_achievement_id=user_achievement_ids(),
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        days_ago=st.integers(min_value=0, max_value=365),
    )
    def test_user_achievement_unlock_age_is_accurate(
        self, user_achievement_id, user_id, achievement_id, days_ago
    ):
        """Test that unlock age calculation is accurate"""
        unlocked_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        user_achievement = UserAchievement(
            user_achievement_id=user_achievement_id,
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=unlocked_at,
        )

        calculated_age = user_achievement.get_unlock_age_days()

        # Should be within 1 day of expected (accounting for execution time)
        assert abs(calculated_age - days_ago) <= 1

    @given(
        user_achievement_id=user_achievement_ids(),
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        days_ago=st.integers(min_value=0, max_value=365),
        threshold=st.integers(min_value=1, max_value=30),
    )
    def test_user_achievement_recent_unlock_detection_is_consistent(
        self, user_achievement_id, user_id, achievement_id, days_ago, threshold
    ):
        """Test that recent unlock detection is consistent"""
        unlocked_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        user_achievement = UserAchievement(
            user_achievement_id=user_achievement_id,
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=unlocked_at,
        )

        is_recent = user_achievement.is_recent_unlock(threshold)

        # Should be recent if days_ago <= threshold
        if days_ago <= threshold:
            assert is_recent
        else:
            assert not is_recent


class TestAchievementProgressProperties:
    """Property-based tests for AchievementProgress entity"""

    @given(
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        progress_percentage=st.floats(min_value=0.0, max_value=100.0),
        is_eligible=st.booleans(),
    )
    def test_achievement_progress_creation_always_valid_with_valid_inputs(
        self, user_id, achievement_id, progress_percentage, is_eligible
    ):
        """Test that achievement progress creation always succeeds with valid inputs"""
        progress = AchievementProgress(
            user_id=user_id,
            achievement_id=achievement_id,
            progress_percentage=progress_percentage,
            last_updated=datetime.now(timezone.utc),
            is_eligible=is_eligible,
        )

        assert progress.user_id == user_id
        assert progress.achievement_id == achievement_id
        assert progress.progress_percentage == progress_percentage
        assert progress.is_eligible == is_eligible

    @given(
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        initial_progress=st.floats(min_value=0.0, max_value=100.0),
        new_progress=st.floats(min_value=0.0, max_value=100.0),
        is_eligible=st.booleans(),
    )
    def test_achievement_progress_update_maintains_invariants(
        self, user_id, achievement_id, initial_progress, new_progress, is_eligible
    ):
        """Test that progress updates maintain invariants"""
        progress = AchievementProgress(
            user_id=user_id,
            achievement_id=achievement_id,
            progress_percentage=initial_progress,
            last_updated=datetime.now(timezone.utc) - timedelta(hours=1),
            is_eligible=False,
        )

        original_update_time = progress.last_updated

        progress.update_progress(
            new_percentage=new_progress, missing_reqs=[], eligible=is_eligible
        )

        # Progress should be updated
        assert progress.progress_percentage == new_progress
        assert progress.is_eligible == is_eligible

        # Update time should be more recent
        assert progress.last_updated > original_update_time

    @given(
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        progress_percentage=st.floats(min_value=0.0, max_value=100.0),
        threshold=st.floats(min_value=0.0, max_value=100.0),
    )
    def test_achievement_progress_close_to_completion_is_consistent(
        self, user_id, achievement_id, progress_percentage, threshold
    ):
        """Test that close to completion detection is consistent"""
        progress = AchievementProgress(
            user_id=user_id,
            achievement_id=achievement_id,
            progress_percentage=progress_percentage,
            last_updated=datetime.now(timezone.utc),
        )

        is_close = progress.is_close_to_completion(threshold)

        # Should be close if progress >= threshold
        if progress_percentage >= threshold:
            assert is_close
        else:
            assert not is_close

    @given(
        user_id=user_ids(),
        achievement_id=achievement_ids(),
        progress_percentage=st.floats(min_value=0.0, max_value=100.0),
        is_eligible=st.booleans(),
    )
    def test_achievement_progress_completion_estimate_is_reasonable(
        self, user_id, achievement_id, progress_percentage, is_eligible
    ):
        """Test that completion estimates are reasonable"""
        progress = AchievementProgress(
            user_id=user_id,
            achievement_id=achievement_id,
            progress_percentage=progress_percentage,
            last_updated=datetime.now(timezone.utc),
            is_eligible=is_eligible,
        )

        estimate = progress.get_completion_estimate()
        valid_estimates = [
            "Ready to unlock!",
            "Almost there!",
            "Close to completion",
            "Halfway there",
            "Making progress",
            "Just getting started",
        ]

        assert estimate in valid_estimates

        # If eligible, should be ready to unlock
        if is_eligible:
            assert estimate == "Ready to unlock!"


class TestValueObjectProperties:
    """Property-based tests for value objects"""

    @given(st.integers(min_value=1, max_value=1000000))
    def test_achievement_id_always_positive(self, value):
        """Test that AchievementId always accepts positive values"""
        achievement_id = AchievementId(value)
        assert achievement_id.value == value
        assert achievement_id.value > 0

    @given(st.integers(max_value=0))
    def test_achievement_id_rejects_non_positive(self, value):
        """Test that AchievementId rejects non-positive values"""
        with pytest.raises(ValueError):
            AchievementId(value)

    @given(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    def test_achievement_name_accepts_valid_strings(self, name):
        """Test that AchievementName accepts valid strings"""
        achievement_name = AchievementName(name)
        assert achievement_name.value == name

    @given(st.text(min_size=201))
    def test_achievement_name_rejects_long_strings(self, name):
        """Test that AchievementName rejects strings over 200 characters"""
        with pytest.raises(ValueError):
            AchievementName(name)

    @given(st.integers(min_value=0, max_value=50000))
    def test_experience_reward_accepts_valid_range(self, value):
        """Test that ExperienceReward accepts valid range"""
        reward = ExperienceReward(value, max_value=50000)
        assert reward.value == value
        assert 0 <= reward.value <= 50000

    @given(st.integers(min_value=50001))
    def test_experience_reward_rejects_excessive_values(self, value):
        """Test that ExperienceReward rejects excessive values"""
        with pytest.raises(ValueError):
            ExperienceReward(value, max_value=50000)

    @given(st.integers(min_value=1, max_value=100))
    def test_required_level_accepts_valid_range(self, value):
        """Test that RequiredLevel accepts valid range"""
        level = RequiredLevel(value)
        assert level.value == value
        assert 1 <= level.value <= 100

    @given(st.integers(max_value=0))
    def test_required_level_rejects_zero_or_negative(self, value):
        """Test that RequiredLevel rejects zero or negative values"""
        with pytest.raises(ValueError):
            RequiredLevel(value)

    @given(st.integers(min_value=0, max_value=10000))
    def test_required_quest_completions_accepts_valid_range(self, value):
        """Test that RequiredQuestCompletions accepts valid range"""
        completions = RequiredQuestCompletions(value)
        assert completions.value == value
        assert 0 <= completions.value <= 10000

    @given(st.integers(max_value=-1))
    def test_required_quest_completions_rejects_negative(self, value):
        """Test that RequiredQuestCompletions rejects negative values"""
        with pytest.raises(ValueError):
            RequiredQuestCompletions(value)
