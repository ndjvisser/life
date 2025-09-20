"""
Stats domain value objects - immutable objects that represent concepts.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union


class StatCategory(Enum):
    """Categories for life stats."""

    HEALTH = "health"
    WEALTH = "wealth"
    RELATIONSHIPS = "relationships"


class CoreStatType(Enum):
    """Types of core RPG stats."""

    STRENGTH = "strength"
    ENDURANCE = "endurance"
    AGILITY = "agility"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


@dataclass(frozen=True)
class StatValue:
    """Value object for stat values with validation."""

    value: int

    def __post_init__(self):
        """
        Validate the StatValue after construction.

        Ensures the `value` attribute is an int and within the inclusive range 1–100.

        Raises:
            ValueError: If `value` is not an int or is outside the allowed range.
        """
        if not isinstance(self.value, int):
            raise ValueError("Stat value must be an integer")
        if not 1 <= self.value <= 100:
            raise ValueError("Stat value must be between 1 and 100")

    def increase(self, amount: int) -> "StatValue":
        """Increase stat value by amount, capped at 100."""
        new_value = min(100, self.value + amount)
        return StatValue(new_value)

    def decrease(self, amount: int) -> "StatValue":
        """
        Return a new StatValue decreased by the given amount, floored at 1.

        The method does not mutate the original instance; it returns a new StatValue whose value is max(1, self.value - amount).

        Parameters:
            amount (int): Amount to subtract from the current stat value.

        Returns:
            StatValue: New instance with the decreased (and clamped) value.
        """
        new_value = max(1, self.value - amount)
        return StatValue(new_value)

    def set_to(self, new_value: int) -> "StatValue":
        """
        Return a new StatValue set to `new_value`.

        `new_value` must be an int between 1 and 100 (inclusive); the constructor validation is applied and a ValueError is raised for invalid input.

        Parameters:
            new_value (int): Target stat value (1–100).

        Returns:
            StatValue: A new immutable StatValue with the requested value.
        """
        return StatValue(new_value)


@dataclass(frozen=True)
class ExperiencePoints:
    """Value object for experience points with validation."""

    value: int

    def __post_init__(self):
        """
        Validate the ExperiencePoints value after object construction.

        Ensures `self.value` is an int and within the allowed range [0, 2**31 - 1]. Raises a ValueError with a specific message if the value is not an integer, is negative, or exceeds the maximum allowed.
        Raises:
            ValueError: If `self.value` is not an int, is negative, or is greater than 2**31 - 1.
        """
        if not isinstance(self.value, int):
            raise ValueError("Experience points must be an integer")
        if self.value < 0:
            raise ValueError("Experience points cannot be negative")
        if self.value > 2**31 - 1:
            raise ValueError("Experience points exceed maximum value")

    def add(self, points: int) -> "ExperiencePoints":
        """
        Return a new ExperiencePoints with `points` added to the current value.

        Parameters:
            points (int): Positive number of experience points to add. The result is capped at 2**31 - 1.

        Returns:
            ExperiencePoints: New instance with the updated value.

        Raises:
            ValueError: If `points` is not a positive integer.
        """
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Points to add must be a positive integer")

        new_value = min(self.value + points, 2**31 - 1)
        return ExperiencePoints(new_value)

    def calculate_level(self) -> int:
        """
        Return the character level derived from the stored experience points.

        Each 1000 XP yields one additional level; the formula used is (value // 1000) + 1.
        The result is always at least 1.

        Returns:
            int: Calculated level (>= 1).
        """
        return max(1, (self.value // 1000) + 1)


@dataclass(frozen=True)
class LifeStatValue:
    """Value object for life stat values with decimal precision."""

    value: Decimal

    def __post_init__(self):
        """
        Validate and normalize the stored value to a Decimal after dataclass initialization.

        Performs two actions:
        - Raises ValueError if `value` is not an int, float, or Decimal.
        - If `value` is an int or float, replaces it with an equivalent Decimal (constructed from str(value)) to preserve precision.
        """
        if not isinstance(self.value, (int, float, Decimal)):
            raise ValueError("Life stat value must be a number")

        # Convert to Decimal if needed
        if isinstance(self.value, (int, float)):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    def add(self, amount: Union[int, float, Decimal]) -> "LifeStatValue":
        """
        Return a new LifeStatValue equal to this value plus `amount`.

        `amount` may be an int, float, or Decimal; ints/floats are converted to Decimal before addition. The method does not mutate the original instance and returns a new LifeStatValue.
        """
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        return LifeStatValue(self.value + amount)

    def subtract(self, amount: Union[int, float, Decimal]) -> "LifeStatValue":
        """
        Return a new LifeStatValue with `amount` subtracted from this value.

        Parameters:
            amount (int | float | Decimal): Amount to subtract; ints/floats are converted to Decimal.
        Returns:
            LifeStatValue: New instance with the result, clamped to a minimum of 0 (original is unchanged).
        """
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        return LifeStatValue(max(Decimal("0"), self.value - amount))

    def multiply(self, factor: Union[int, float, Decimal]) -> "LifeStatValue":
        """
        Return a new LifeStatValue representing this value multiplied by `factor`.

        `factor` may be an int, float, or Decimal; ints/floats are converted to Decimal using
        str() to preserve numeric precision. This method does not mutate the original instance.

        Parameters:
            factor (int | float | Decimal): Multiplier applied to the current value.

        Returns:
            LifeStatValue: New instance whose value equals self.value * factor.
        """
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        return LifeStatValue(self.value * factor)

    def to_float(self) -> float:
        """
        Return the numeric value as a Python float suitable for display.

        Converts the underlying Decimal value to float. Note that this may lose precision compared to the Decimal representation.

        Returns:
            float: The stat value as a float.
        """
        return float(self.value)


@dataclass(frozen=True)
class StatTarget:
    """Value object for stat targets."""

    value: Decimal
    unit: str = ""

    def __post_init__(self):
        """
        Validate and normalize the target `value` to a Decimal.

        Ensures `value` is numeric (int, float, or Decimal). If `value` is an int or float it is converted to a Decimal (using `Decimal(str(value))`) and written back onto the frozen dataclass. Raises ValueError when `value` is not a number.
        """
        if not isinstance(self.value, (int, float, Decimal)):
            raise ValueError("Target value must be a number")

        if isinstance(self.value, (int, float)):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    def is_achieved_by(self, current_value: Union[int, float, Decimal]) -> bool:
        """
        Return True if the provided current value meets or exceeds the target.

        Accepts int, float, or Decimal; numeric inputs are converted to Decimal for comparison.
        """
        if isinstance(current_value, (int, float)):
            current_value = Decimal(str(current_value))
        return current_value >= self.value

    def progress_percentage(self, current_value: Union[int, float, Decimal]) -> float:
        """
        Return the progress toward this StatTarget as a percentage.

        Accepts current_value as int, float, or Decimal. If the target value is zero the function returns 100.0 when current_value >= 0, otherwise 0.0. The computed progress is (current_value / target) * 100, clamped to a maximum of 100 and rounded to two decimal places.

        Parameters:
            current_value (int | float | Decimal): The current measured value to compare against the target.

        Returns:
            float: Progress percentage in the range [0.0, 100.0], rounded to two decimals.
        """
        if isinstance(current_value, (int, float)):
            current_value = Decimal(str(current_value))

        if self.value == 0:
            return 100.0 if current_value >= 0 else 0.0

        progress = min(100.0, float((current_value / self.value) * 100))
        return round(progress, 2)

    def distance_from(self, current_value: Union[int, float, Decimal]) -> Decimal:
        """
        Return the non-negative Decimal distance from `current_value` to the target.

        Accepts an int, float, or Decimal for `current_value` (int/float are converted to Decimal). Returns target - current_value as a Decimal, floored at 0 when `current_value` is greater than or equal to the target.
        """
        if isinstance(current_value, (int, float)):
            current_value = Decimal(str(current_value))

        return max(Decimal("0"), self.value - current_value)


@dataclass(frozen=True)
class StatChange:
    """Value object representing a change in stat value."""

    old_value: Decimal
    new_value: Decimal
    reason: str = ""

    def __post_init__(self):
        # Ensure values are Decimal
        """
        Normalize numeric inputs to Decimal after dataclass initialization.

        If either `old_value` or `new_value` was provided as an int or float, convert it to a Decimal (using Decimal(str(...))) and set the attribute on the frozen dataclass so both values are guaranteed to be Decimals thereafter.
        """
        if isinstance(self.old_value, (int, float)):
            object.__setattr__(self, "old_value", Decimal(str(self.old_value)))
        if isinstance(self.new_value, (int, float)):
            object.__setattr__(self, "new_value", Decimal(str(self.new_value)))

    @property
    def change_amount(self) -> Decimal:
        """
        Difference between new_value and old_value as a Decimal (computed as new_value - old_value).
        Can be positive, negative, or zero.
        """
        return self.new_value - self.old_value

    @property
    def is_increase(self) -> bool:
        """
        Return True if the change represents an increase (new_value > old_value).

        This checks the computed `change_amount` (new_value - old_value) and returns True when it is greater than zero.
        """
        return self.change_amount > 0

    @property
    def is_decrease(self) -> bool:
        """Check if this is a decrease."""
        return self.change_amount < 0

    @property
    def percentage_change(self) -> float:
        """
        Return the signed percentage change from old_value to new_value as a float.

        If old_value is zero, returns 100.0 when new_value > 0 and 0.0 when new_value == 0. The result is (new_value - old_value) / old_value * 100 and may be negative for decreases. Values are computed from Decimal fields but returned as a float.
        """
        if self.old_value == 0:
            return 100.0 if self.new_value > 0 else 0.0

        return float((self.change_amount / self.old_value) * 100)

    def is_significant(self, threshold_percentage: float = 10.0) -> bool:
        """
        Return whether the change's absolute percentage change meets or exceeds the given threshold.

        Parameters:
            threshold_percentage (float): Threshold in percent (e.g., 10.0 for 10%). Defaults to 10.0.

        Returns:
            bool: True if abs(percentage_change) >= threshold_percentage, otherwise False.
        """
        return abs(self.percentage_change) >= threshold_percentage
