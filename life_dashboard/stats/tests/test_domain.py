"""
Tests for stats domain layer - pure Python business logic tests.
"""

from decimal import Decimal

import pytest

from ..domain.entities import CoreStat, LifeStat, StatHistory
from ..domain.value_objects import (
    LifeStatValue,
    StatTarget,
    StatValue,
)


class TestCoreStat:
    """Test CoreStat domain entity."""

    def test_create_core_stat(self):
        """Test creating a core stat."""
        stat = CoreStat(user_id=1)

        assert stat.user_id == 1
        assert stat.strength == 10
        assert stat.experience_points == 0
        assert stat.level == 1

    def test_create_with_custom_values(self):
        """Test creating core stat with custom values."""
        stat = CoreStat(user_id=1, strength=15, intelligence=20, experience_points=2500)

        assert stat.strength == 15
        assert stat.intelligence == 20
        assert stat.experience_points == 2500
        assert stat.level == 3  # 2500 XP = level 3

    def test_invalid_stat_values(self):
        """Test validation of stat values."""
        with pytest.raises(
            ValueError, match="strength must be an integer between 1 and 100"
        ):
            CoreStat(user_id=1, strength=0)

        with pytest.raises(
            ValueError, match="intelligence must be an integer between 1 and 100"
        ):
            CoreStat(user_id=1, intelligence=101)

    def test_update_stat(self):
        """Test updating a stat value."""
        stat = CoreStat(user_id=1)

        new_value = stat.update_stat("strength", 15)

        assert new_value == 15
        assert stat.strength == 15
        assert stat.updated_at is not None

    def test_update_invalid_stat(self):
        """Test updating invalid stat."""
        stat = CoreStat(user_id=1)

        with pytest.raises(ValueError, match="Invalid stat name"):
            stat.update_stat("invalid_stat", 15)

        with pytest.raises(
            ValueError, match="Stat value must be an integer between 1 and 100"
        ):
            stat.update_stat("strength", 0)

    def test_add_experience(self):
        """Test adding experience points."""
        stat = CoreStat(user_id=1)

        new_level, level_up = stat.add_experience(500)

        assert stat.experience_points == 500
        assert stat.level == 1
        assert new_level == 1
        assert level_up is False

    def test_add_experience_level_up(self):
        """Test level up when adding experience."""
        stat = CoreStat(user_id=1)

        new_level, level_up = stat.add_experience(1500)

        assert stat.experience_points == 1500
        assert stat.level == 2
        assert new_level == 2
        assert level_up is True

    def test_add_experience_invalid(self):
        """Test adding invalid experience."""
        stat = CoreStat(user_id=1)

        with pytest.raises(
            ValueError, match="Experience points must be a positive integer"
        ):
            stat.add_experience(-100)

        with pytest.raises(
            ValueError, match="Experience points must be a positive integer"
        ):
            stat.add_experience(0)

    def test_stat_calculations(self):
        """Test stat calculation methods."""
        stat = CoreStat(
            user_id=1,
            strength=15,
            endurance=12,
            agility=18,
            intelligence=20,
            wisdom=14,
            charisma=16,
        )

        assert stat.get_stat_total() == 95
        assert stat.get_stat_average() == 95 / 6

    def test_to_dict(self):
        """Test converting to dictionary."""
        stat = CoreStat(user_id=1, strength=15)
        result = stat.to_dict()

        assert result["user_id"] == 1
        assert result["strength"] == 15
        assert result["stat_total"] == stat.get_stat_total()
        assert result["stat_average"] == stat.get_stat_average()


class TestLifeStat:
    """Test LifeStat domain entity."""

    def test_create_life_stat(self):
        """Test creating a life stat."""
        stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70.5"),
            unit="kg",
        )

        assert stat.user_id == 1
        assert stat.category == "health"
        assert stat.name == "weight"
        assert stat.value == Decimal("70.5")
        assert stat.unit == "kg"

    def test_invalid_category(self):
        """Test invalid category validation."""
        with pytest.raises(ValueError, match="Category must be one of"):
            LifeStat(user_id=1, category="invalid", name="test")

    def test_update_value(self):
        """Test updating stat value."""
        stat = LifeStat(
            user_id=1, category="health", name="weight", value=Decimal("70")
        )

        new_value = stat.update_value(Decimal("72.5"), "Weight gain")

        assert new_value == Decimal("72.5")
        assert stat.value == Decimal("72.5")
        assert stat.notes == "Weight gain"
        assert stat.last_updated is not None

    def test_set_target(self):
        """Test setting target value."""
        stat = LifeStat(
            user_id=1, category="health", name="weight", value=Decimal("70")
        )

        stat.set_target(Decimal("65"))

        assert stat.target == Decimal("65")
        assert stat.last_updated is not None

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70"),
            target=Decimal("65"),
        )

        # Progress towards weight loss target
        # Current: 70, Target: 65, so we need to lose 5kg
        # Progress is capped at 100% even when over target
        progress = stat.progress_percentage()
        assert progress == 100.0  # Capped at 100% even when over target

    def test_is_target_achieved(self):
        """Test target achievement check."""
        stat = LifeStat(
            user_id=1,
            category="wealth",
            name="savings",
            value=Decimal("5000"),
            target=Decimal("10000"),
        )

        assert not stat.is_target_achieved()

        stat.update_value(Decimal("12000"))
        assert stat.is_target_achieved()

    def test_distance_to_target(self):
        """Test distance to target calculation."""
        stat = LifeStat(
            user_id=1,
            category="wealth",
            name="savings",
            value=Decimal("5000"),
            target=Decimal("10000"),
        )

        distance = stat.distance_to_target()
        assert distance == Decimal("5000")

    def test_to_dict(self):
        """Test converting to dictionary."""
        stat = LifeStat(
            user_id=1,
            category="health",
            name="weight",
            value=Decimal("70"),
            target=Decimal("65"),
            unit="kg",
        )

        result = stat.to_dict()

        assert result["user_id"] == 1
        assert result["category"] == "health"
        assert result["name"] == "weight"
        assert result["value"] == 70.0
        assert result["target"] == 65.0
        assert result["unit"] == "kg"
        assert "progress_percentage" in result
        assert "is_target_achieved" in result


class TestStatHistory:
    """Test StatHistory domain entity."""

    def test_create_stat_history(self):
        """Test creating stat history."""
        history = StatHistory(
            user_id=1,
            stat_type="core",
            stat_name="strength",
            old_value=Decimal("10"),
            new_value=Decimal("15"),
            change_reason="Training",
        )

        assert history.user_id == 1
        assert history.stat_type == "core"
        assert history.stat_name == "strength"
        assert history.old_value == Decimal("10")
        assert history.new_value == Decimal("15")
        assert history.change_amount == Decimal("5")
        assert history.change_reason == "Training"
        assert history.timestamp is not None

    def test_change_properties(self):
        """Test change property calculations."""
        history = StatHistory(
            user_id=1,
            stat_type="life",
            stat_name="weight",
            old_value=Decimal("70"),
            new_value=Decimal("68"),
        )

        assert history.is_decrease
        assert not history.is_increase
        assert history.change_amount == Decimal("-2")

        # Percentage change: -2/70 * 100 ≈ -2.86%
        assert abs(history.percentage_change + 2.86) < 0.1

    def test_zero_old_value(self):
        """Test percentage change with zero old value."""
        history = StatHistory(
            user_id=1,
            stat_type="life",
            stat_name="savings",
            old_value=Decimal("0"),
            new_value=Decimal("1000"),
        )

        assert history.percentage_change is None  # Can't calculate percentage from zero

    def test_to_dict(self):
        """Test converting to dictionary."""
        history = StatHistory(
            user_id=1,
            stat_type="core",
            stat_name="strength",
            old_value=Decimal("10"),
            new_value=Decimal("15"),
        )

        result = history.to_dict()

        assert result["user_id"] == 1
        assert result["stat_type"] == "core"
        assert result["stat_name"] == "strength"
        assert result["old_value"] == 10.0
        assert result["new_value"] == 15.0
        assert result["change_amount"] == 5.0
        assert result["is_increase"] is True
        assert result["is_decrease"] is False


class TestStatValue:
    """Test StatValue value object."""

    def test_create_valid_stat_value(self):
        """Test creating valid stat value."""
        stat_value = StatValue(50)
        assert stat_value.value == 50

    def test_create_invalid_stat_value(self):
        """Test creating invalid stat value."""
        with pytest.raises(ValueError, match="Stat value must be an integer"):
            StatValue("50")

        with pytest.raises(ValueError, match="Stat value must be between 1 and 100"):
            StatValue(0)

        with pytest.raises(ValueError, match="Stat value must be between 1 and 100"):
            StatValue(101)

    def test_increase_stat_value(self):
        """Test increasing stat value."""
        stat_value = StatValue(50)
        new_value = stat_value.increase(20)

        assert new_value.value == 70
        assert stat_value.value == 50  # Original unchanged

    def test_increase_stat_value_capped(self):
        """Test increasing stat value with cap."""
        stat_value = StatValue(95)
        new_value = stat_value.increase(10)

        assert new_value.value == 100  # Capped at 100

    def test_decrease_stat_value(self):
        """Test decreasing stat value."""
        stat_value = StatValue(50)
        new_value = stat_value.decrease(20)

        assert new_value.value == 30

    def test_decrease_stat_value_floored(self):
        """Test decreasing stat value with floor."""
        stat_value = StatValue(5)
        new_value = stat_value.decrease(10)

        assert new_value.value == 1  # Floored at 1


class TestLifeStatValue:
    """Test LifeStatValue value object."""

    def test_create_life_stat_value(self):
        """Test creating life stat value."""
        value = LifeStatValue(Decimal("42.5"))
        assert value.value == Decimal("42.5")

    def test_create_from_int(self):
        """Test creating from integer."""
        value = LifeStatValue(42)
        assert value.value == Decimal("42")

    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        value = LifeStatValue(Decimal("10.5"))

        # Addition
        new_value = value.add(5.5)
        assert new_value.value == Decimal("16.0")

        # Subtraction
        new_value = value.subtract(2.5)
        assert new_value.value == Decimal("8.0")

        # Subtraction with floor at 0
        new_value = value.subtract(15)
        assert new_value.value == Decimal("0")

        # Multiplication
        new_value = value.multiply(2)
        assert new_value.value == Decimal("21.0")

    def test_to_float(self):
        """Test converting to float."""
        value = LifeStatValue(Decimal("42.75"))
        assert value.to_float() == 42.75


class TestStatTarget:
    """Test StatTarget value object."""

    def test_create_stat_target(self):
        """Test creating stat target."""
        target = StatTarget(Decimal("100"), "kg")
        assert target.value == Decimal("100")
        assert target.unit == "kg"

    def test_is_achieved_by(self):
        """Test achievement check."""
        target = StatTarget(Decimal("100"))

        assert target.is_achieved_by(100)
        assert target.is_achieved_by(105)
        assert not target.is_achieved_by(95)

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        target = StatTarget(Decimal("100"))

        assert target.progress_percentage(50) == 50.0
        assert target.progress_percentage(100) == 100.0
        assert target.progress_percentage(150) == 100.0  # Capped at 100%

    def test_distance_from(self):
        """Test distance calculation."""
        target = StatTarget(Decimal("100"))

        assert target.distance_from(75) == Decimal("25")
        assert target.distance_from(100) == Decimal("0")
        assert target.distance_from(105) == Decimal("0")  # No negative distance
