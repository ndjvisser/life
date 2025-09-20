"""
Property-based tests for stats domain layer using Hypothesis.

These tests generate random inputs to verify domain invariants and edge cases.
"""

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ..domain.entities import CoreStat, LifeStat
from ..domain.value_objects import (
    ExperiencePoints,
    LifeStatValue,
    StatChange,
    StatTarget,
    StatValue,
)


class TestCoreStatProperties:
    """Property-based tests for CoreStat domain entity."""

    @given(
        user_id=st.integers(min_value=1, max_value=1000000),
        strength=st.integers(min_value=1, max_value=100),
        endurance=st.integers(min_value=1, max_value=100),
        agility=st.integers(min_value=1, max_value=100),
        intelligence=st.integers(min_value=1, max_value=100),
        wisdom=st.integers(min_value=1, max_value=100),
        charisma=st.integers(min_value=1, max_value=100),
        experience_points=st.integers(min_value=0, max_value=2**31 - 1),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_core_stat_invariants(
        self,
        user_id,
        strength,
        endurance,
        agility,
        intelligence,
        wisdom,
        charisma,
        experience_points,
    ):
        """Test that CoreStat maintains invariants with any valid input."""
        stat = CoreStat(
            user_id=user_id,
            strength=strength,
            endurance=endurance,
            agility=agility,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            experience_points=experience_points,
        )

        # Invariant: All stats are within valid range
        assert 1 <= stat.strength <= 100
        assert 1 <= stat.endurance <= 100
        assert 1 <= stat.agility <= 100
        assert 1 <= stat.intelligence <= 100
        assert 1 <= stat.wisdom <= 100
        assert 1 <= stat.charisma <= 100

        # Invariant: Level is correctly calculated from experience
        expected_level = max(1, (experience_points // 1000) + 1)
        assert stat.level == expected_level

        # Invariant: Stat total is sum of all stats
        expected_total = (
            strength + endurance + agility + intelligence + wisdom + charisma
        )
        assert stat.get_stat_total() == expected_total

        # Invariant: Stat average is total divided by 6
        assert stat.get_stat_average() == expected_total / 6

    @given(
        stat_name=st.sampled_from(
            ["strength", "endurance", "agility", "intelligence", "wisdom", "charisma"]
        ),
        initial_value=st.integers(min_value=1, max_value=100),
        new_value=st.integers(min_value=1, max_value=100),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_update_stat_properties(self, stat_name, initial_value, new_value):
        """Test stat update properties."""
        stat = CoreStat(user_id=1, **{stat_name: initial_value})

        result = stat.update_stat(stat_name, new_value)

        # Property: Update returns the new value
        assert result == new_value

        # Property: Stat is actually updated
        assert getattr(stat, stat_name) == new_value

        # Property: Updated timestamp is set
        assert stat.updated_at is not None

    @given(
        experience_to_add=st.integers(min_value=1, max_value=1000000),
        initial_experience=st.integers(min_value=0, max_value=1000000),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_add_experience_properties(self, experience_to_add, initial_experience):
        """Test experience addition properties."""
        stat = CoreStat(user_id=1, experience_points=initial_experience)
        old_level = stat.level

        new_level, level_up = stat.add_experience(experience_to_add)

        # Property: Experience increases (unless capped)
        max_experience = 2**31 - 1
        expected_experience = min(
            initial_experience + experience_to_add, max_experience
        )
        assert stat.experience_points == expected_experience

        # Property: Level is recalculated correctly
        expected_level = max(1, (expected_experience // 1000) + 1)
        assert stat.level == expected_level
        assert new_level == expected_level

        # Property: Level up flag is correct
        assert level_up == (new_level > old_level)


class TestLifeStatProperties:
    """Property-based tests for LifeStat domain entity."""

    @given(
        user_id=st.integers(min_value=1, max_value=1000000),
        category=st.sampled_from(["health", "wealth", "relationships"]),
        name=st.text(min_size=1, max_size=50),
        value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000000"), places=2
        ),
        target=st.one_of(
            st.none(),
            st.decimals(min_value=Decimal("0"), max_value=Decimal("1000000"), places=2),
        ),
        unit=st.text(max_size=20),
        notes=st.text(max_size=200),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_life_stat_invariants(
        self, user_id, category, name, value, target, unit, notes
    ):
        """Test that LifeStat maintains invariants with any valid input."""
        stat = LifeStat(
            user_id=user_id,
            category=category,
            name=name,
            value=value,
            target=target,
            unit=unit,
            notes=notes,
        )

        # Invariant: Category is normalized to lowercase
        assert stat.category == category.lower()

        # Invariant: Value is a Decimal
        assert isinstance(stat.value, Decimal)

        # Invariant: Target is None or Decimal
        assert stat.target is None or isinstance(stat.target, Decimal)

        # Invariant: Progress percentage is between 0 and 100
        progress = stat.progress_percentage()
        assert 0.0 <= progress <= 100.0

        # Invariant: Target achievement is consistent with progress
        if target is not None and target > 0:
            is_achieved = stat.is_target_achieved()
            if is_achieved:
                assert progress == 100.0 or stat.value >= target

    @given(
        initial_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000"), places=2
        ),
        new_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000"), places=2
        ),
        notes=st.text(max_size=100),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_update_value_properties(self, initial_value, new_value, notes):
        """Test value update properties."""
        stat = LifeStat(
            user_id=1,
            category="health",
            name="test",
            value=initial_value,
        )

        result = stat.update_value(new_value, notes)

        # Property: Update returns the new value as Decimal
        assert result == new_value
        assert isinstance(result, Decimal)

        # Property: Value is actually updated
        assert stat.value == new_value

        # Property: Notes are updated if provided
        if notes:
            assert stat.notes == notes

        # Property: Last updated timestamp is set
        assert stat.last_updated is not None


class TestStatValueProperties:
    """Property-based tests for StatValue value object."""

    @given(value=st.integers(min_value=1, max_value=100))
    @pytest.mark.property
    @pytest.mark.domain
    def test_stat_value_creation(self, value):
        """Test StatValue creation with valid values."""
        stat_value = StatValue(value)
        assert stat_value.value == value

    @given(
        initial_value=st.integers(min_value=1, max_value=100),
        increase_amount=st.integers(min_value=0, max_value=200),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_increase_properties(self, initial_value, increase_amount):
        """Test increase operation properties."""
        stat_value = StatValue(initial_value)
        new_value = stat_value.increase(increase_amount)

        # Property: Result is capped at 100
        assert new_value.value <= 100

        # Property: Result is at least the initial value
        assert new_value.value >= initial_value

        # Property: Original is unchanged (immutability)
        assert stat_value.value == initial_value

        # Property: Exact calculation when not capped
        if initial_value + increase_amount <= 100:
            assert new_value.value == initial_value + increase_amount
        else:
            assert new_value.value == 100

    @given(
        initial_value=st.integers(min_value=1, max_value=100),
        decrease_amount=st.integers(min_value=0, max_value=200),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_decrease_properties(self, initial_value, decrease_amount):
        """Test decrease operation properties."""
        stat_value = StatValue(initial_value)
        new_value = stat_value.decrease(decrease_amount)

        # Property: Result is floored at 1
        assert new_value.value >= 1

        # Property: Result is at most the initial value
        assert new_value.value <= initial_value

        # Property: Original is unchanged (immutability)
        assert stat_value.value == initial_value

        # Property: Exact calculation when not floored
        if initial_value - decrease_amount >= 1:
            assert new_value.value == initial_value - decrease_amount
        else:
            assert new_value.value == 1


class TestExperiencePointsProperties:
    """Property-based tests for ExperiencePoints value object."""

    @given(value=st.integers(min_value=0, max_value=2**31 - 1))
    @pytest.mark.property
    @pytest.mark.domain
    def test_experience_points_creation(self, value):
        """Test ExperiencePoints creation with valid values."""
        xp = ExperiencePoints(value)
        assert xp.value == value

    @given(
        initial_xp=st.integers(min_value=0, max_value=1000000),
        points_to_add=st.integers(min_value=1, max_value=1000000),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_add_experience_properties(self, initial_xp, points_to_add):
        """Test experience addition properties."""
        xp = ExperiencePoints(initial_xp)
        new_xp = xp.add(points_to_add)

        # Property: Result is capped at maximum
        max_xp = 2**31 - 1
        assert new_xp.value <= max_xp

        # Property: Result is at least the initial value
        assert new_xp.value >= initial_xp

        # Property: Original is unchanged (immutability)
        assert xp.value == initial_xp

        # Property: Exact calculation when not capped
        if initial_xp + points_to_add <= max_xp:
            assert new_xp.value == initial_xp + points_to_add
        else:
            assert new_xp.value == max_xp

    @given(xp_value=st.integers(min_value=0, max_value=100000))
    @pytest.mark.property
    @pytest.mark.domain
    def test_level_calculation_properties(self, xp_value):
        """Test level calculation properties."""
        xp = ExperiencePoints(xp_value)
        level = xp.calculate_level()

        # Property: Level is always at least 1
        assert level >= 1

        # Property: Level calculation is consistent
        expected_level = max(1, (xp_value // 1000) + 1)
        assert level == expected_level

        # Property: Level increases with XP
        if xp_value >= 1000:
            lower_xp = ExperiencePoints(xp_value - 1000)
            assert level >= lower_xp.calculate_level()


class TestLifeStatValueProperties:
    """Property-based tests for LifeStatValue value object."""

    @given(
        value=st.one_of(
            st.integers(min_value=0, max_value=1000000),
            st.floats(
                min_value=0.0,
                max_value=1000000.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            st.decimals(min_value=Decimal("0"), max_value=Decimal("1000000"), places=2),
        )
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_life_stat_value_creation(self, value):
        """Test LifeStatValue creation with various numeric types."""
        stat_value = LifeStatValue(value)

        # Property: Value is always stored as Decimal
        assert isinstance(stat_value.value, Decimal)

        # Property: Value is preserved (within Decimal precision)
        if isinstance(value, Decimal):
            assert stat_value.value == value
        else:
            # For int/float, check approximate equality
            assert abs(float(stat_value.value) - float(value)) < 0.01

    @given(
        initial_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000"), places=2
        ),
        amount=st.decimals(min_value=Decimal("0"), max_value=Decimal("1000"), places=2),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_arithmetic_properties(self, initial_value, amount):
        """Test arithmetic operation properties."""
        stat_value = LifeStatValue(initial_value)

        # Addition properties
        added = stat_value.add(amount)
        assert added.value == initial_value + amount
        assert stat_value.value == initial_value  # Immutability

        # Subtraction properties
        subtracted = stat_value.subtract(amount)
        assert subtracted.value >= Decimal("0")  # Floored at 0
        assert stat_value.value == initial_value  # Immutability

        # Multiplication properties
        multiplied = stat_value.multiply(2)
        assert multiplied.value == initial_value * 2
        assert stat_value.value == initial_value  # Immutability


class TestStatTargetProperties:
    """Property-based tests for StatTarget value object."""

    @given(
        target_value=st.decimals(
            min_value=Decimal("0.01"), max_value=Decimal("1000"), places=2
        ),
        current_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1500"), places=2
        ),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_target_achievement_properties(self, target_value, current_value):
        """Test target achievement properties."""
        target = StatTarget(target_value)

        # Property: Achievement is consistent with comparison
        is_achieved = target.is_achieved_by(current_value)
        assert is_achieved == (current_value >= target_value)

        # Property: Progress percentage is between 0 and 100
        progress = target.progress_percentage(current_value)
        assert 0.0 <= progress <= 100.0

        # Property: Progress is 100% when achieved
        if is_achieved:
            assert progress == 100.0

        # Property: Distance is non-negative
        distance = target.distance_from(current_value)
        assert distance >= Decimal("0")

        # Property: Distance is 0 when achieved
        if is_achieved:
            assert distance == Decimal("0")


class TestStatChangeProperties:
    """Property-based tests for StatChange value object."""

    @given(
        old_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000"), places=2
        ),
        new_value=st.decimals(
            min_value=Decimal("0"), max_value=Decimal("1000"), places=2
        ),
        reason=st.text(max_size=100),
    )
    @pytest.mark.property
    @pytest.mark.domain
    def test_stat_change_properties(self, old_value, new_value, reason):
        """Test StatChange properties."""
        change = StatChange(old_value, new_value, reason)

        # Property: Change amount is correctly calculated
        assert change.change_amount == new_value - old_value

        # Property: Increase/decrease flags are consistent
        if new_value > old_value:
            assert change.is_increase
            assert not change.is_decrease
        elif new_value < old_value:
            assert not change.is_increase
            assert change.is_decrease
        else:
            assert not change.is_increase
            assert not change.is_decrease

        # Property: Percentage change is consistent (when old_value > 0)
        if old_value > 0:
            expected_percentage = float((new_value - old_value) / old_value * 100)
            assert abs(change.percentage_change - expected_percentage) < 0.01

        # Property: Significance threshold works correctly
        threshold = 10.0
        is_significant = change.is_significant(threshold)
        assert is_significant == (abs(change.percentage_change) >= threshold)
