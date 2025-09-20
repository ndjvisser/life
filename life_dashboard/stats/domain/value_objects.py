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
        if not isinstance(self.value, int):
            raise ValueError("Stat value must be an integer")
        if not 1 <= self.value <= 100:
            raise ValueError("Stat value must be between 1 and 100")

    def increase(self, amount: int) -> "StatValue":
        """Increase stat value by amount, capped at 100."""
        new_value = min(100, self.value + amount)
        return StatValue(new_value)

    def decrease(self, amount: int) -> "StatValue":
        """Decrease stat value by amount, floored at 1."""
        new_value = max(1, self.value - amount)
        return StatValue(new_value)

    def set_to(self, new_value: int) -> "StatValue":
        """Set to new value with validation."""
        return StatValue(new_value)


@dataclass(frozen=True)
class ExperiencePoints:
    """Value object for experience points with validation."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Experience points must be an integer")
        if self.value < 0:
            raise ValueError("Experience points cannot be negative")
        if self.value > 2**31 - 1:
            raise ValueError("Experience points exceed maximum value")

    def add(self, points: int) -> "ExperiencePoints":
        """Add points and return new ExperiencePoints object."""
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Points to add must be a positive integer")

        new_value = min(self.value + points, 2**31 - 1)
        return ExperiencePoints(new_value)

    def calculate_level(self) -> int:
        """Calculate level based on experience points."""
        return max(1, (self.value // 1000) + 1)


@dataclass(frozen=True)
class LifeStatValue:
    """Value object for life stat values with decimal precision."""

    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, (int, float, Decimal)):
            raise ValueError("Life stat value must be a number")

        # Convert to Decimal if needed
        if isinstance(self.value, (int, float)):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    def add(self, amount: Union[int, float, Decimal]) -> "LifeStatValue":
        """Add amount to value."""
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        return LifeStatValue(self.value + amount)

    def subtract(self, amount: Union[int, float, Decimal]) -> "LifeStatValue":
        """Subtract amount from value."""
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        return LifeStatValue(max(Decimal("0"), self.value - amount))

    def multiply(self, factor: Union[int, float, Decimal]) -> "LifeStatValue":
        """Multiply value by factor."""
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        return LifeStatValue(self.value * factor)

    def to_float(self) -> float:
        """Convert to float for display."""
        return float(self.value)


@dataclass(frozen=True)
class StatTarget:
    """Value object for stat targets."""

    value: Decimal
    unit: str = ""

    def __post_init__(self):
        if not isinstance(self.value, (int, float, Decimal)):
            raise ValueError("Target value must be a number")

        if isinstance(self.value, (int, float)):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    def is_achieved_by(self, current_value: Union[int, float, Decimal]) -> bool:
        """Check if target is achieved by current value."""
        if isinstance(current_value, (int, float)):
            current_value = Decimal(str(current_value))
        return current_value >= self.value

    def progress_percentage(self, current_value: Union[int, float, Decimal]) -> float:
        """Calculate progress percentage towards target."""
        if isinstance(current_value, (int, float)):
            current_value = Decimal(str(current_value))

        if self.value == 0:
            return 100.0 if current_value >= 0 else 0.0

        progress = min(100.0, float((current_value / self.value) * 100))
        return round(progress, 2)

    def distance_from(self, current_value: Union[int, float, Decimal]) -> Decimal:
        """Calculate distance from current value to target."""
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
        if isinstance(self.old_value, (int, float)):
            object.__setattr__(self, "old_value", Decimal(str(self.old_value)))
        if isinstance(self.new_value, (int, float)):
            object.__setattr__(self, "new_value", Decimal(str(self.new_value)))

    @property
    def change_amount(self) -> Decimal:
        """Get the amount of change."""
        return self.new_value - self.old_value

    @property
    def is_increase(self) -> bool:
        """Check if this is an increase."""
        return self.change_amount > 0

    @property
    def is_decrease(self) -> bool:
        """Check if this is a decrease."""
        return self.change_amount < 0

    @property
    def percentage_change(self) -> float:
        """Calculate percentage change."""
        if self.old_value == 0:
            return 100.0 if self.new_value > 0 else 0.0

        return float((self.change_amount / self.old_value) * 100)

    def is_significant(self, threshold_percentage: float = 10.0) -> bool:
        """Check if change is significant based on percentage threshold."""
        return abs(self.percentage_change) >= threshold_percentage
