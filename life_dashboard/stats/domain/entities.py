"""
Stats domain entities - pure Python business logic without Django dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class CoreStat:
    """Pure domain entity for RPG-style core stats."""

    user_id: int

    # RPG attributes
    strength: int = 10
    endurance: int = 10
    agility: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Experience and level
    experience_points: int = 0
    level: int = 1

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """
        Run post-initialization checks and compute derived state.

        Performs validation of all core stat fields (raises ValueError if any stat is invalid) and initializes the entity's level based on the current experience_points.
        """
        self._validate_stats()
        self._calculate_level()

    def _validate_stats(self):
        """
        Validate that each core stat is an integer in the inclusive range 1–100.

        Checks the six core stat attributes: strength, endurance, agility, intelligence, wisdom, and charisma.
        Raises:
            ValueError: if any stat is not an int or is outside 1..100.
        """
        stat_fields = [
            "strength",
            "endurance",
            "agility",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        for stat_field in stat_fields:
            value = getattr(self, stat_field)
            if not isinstance(value, int) or value < 1 or value > 100:
                raise ValueError(f"{stat_field} must be an integer between 1 and 100")

    def _calculate_level(self):
        """
        Compute and set the object's level from experience points.

        Uses integer division to convert experience_points into levels with 1 level per 1000 XP and a minimum level of 1:
        level = max(1, (experience_points // 1000) + 1). Updates self.level in-place.
        """
        self.level = max(1, (self.experience_points // 1000) + 1)

    def update_stat(self, stat_name: str, value: int) -> int:
        """
        Update a single core stat for this CoreStat instance.

        Valid stat names: "strength", "endurance", "agility", "intelligence", "wisdom", "charisma".
        The new value must be an integer in the range [1, 100]. On success the stat is set, updated_at is set to the current UTC time, and the new value is returned.

        Parameters:
            stat_name (str): Name of the stat to update.
            value (int): New stat value (1–100).

        Returns:
            int: The updated stat value.

        Raises:
            ValueError: If `stat_name` is not one of the valid stats or if `value` is not an int in [1, 100].
        """
        valid_stats = [
            "strength",
            "endurance",
            "agility",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        if stat_name not in valid_stats:
            raise ValueError(f"Invalid stat name: {stat_name}")

        if not isinstance(value, int) or value < 1 or value > 100:
            raise ValueError("Stat value must be an integer between 1 and 100")

        setattr(self, stat_name, value)
        self.updated_at = datetime.utcnow()

        return value

    def add_experience(self, points: int) -> tuple[int, bool]:
        """
        Increment the object's experience points, recalculate level, and indicate if a level-up occurred.

        Adds the given positive integer `points` to `experience_points` (capped at 2**31 - 1 to prevent overflow), updates the `level` based on the new total, and sets `updated_at` to the current UTC time.

        Parameters:
            points (int): Positive integer number of experience points to add.

        Returns:
            Tuple[int, bool]: (new_level, level_up_occurred) where `new_level` is the recalculated level and `level_up_occurred` is True if the level increased.

        Raises:
            ValueError: If `points` is not a positive integer.
        """
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Experience points must be a positive integer")

        old_level = self.level

        # Cap experience to prevent overflow
        max_experience = 2**31 - 1
        if self.experience_points + points > max_experience:
            self.experience_points = max_experience
        else:
            self.experience_points += points

        self._calculate_level()
        self.updated_at = datetime.utcnow()

        level_up_occurred = self.level > old_level
        return self.level, level_up_occurred

    def get_stat_total(self) -> int:
        """
        Return the sum of the six core stats (strength, endurance, agility, intelligence, wisdom, charisma).

        Returns:
            int: Total of all core stat values.
        """
        return (
            self.strength
            + self.endurance
            + self.agility
            + self.intelligence
            + self.wisdom
            + self.charisma
        )

    def get_stat_average(self) -> float:
        """
        Return the arithmetic mean of the six core stats.

        Returns:
            float: Average (mean) of strength, endurance, agility, intelligence, wisdom, and charisma.
        """
        return self.get_stat_total() / 6

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the CoreStat suitable for serialization.

        The mapping includes all core fields and derived aggregates:
        - user_id (int)
        - strength, endurance, agility, intelligence, wisdom, charisma (int)
        - experience_points (int)
        - level (int)
        - stat_total (int): sum of the six core stats
        - stat_average (float): average of the six core stats
        - created_at, updated_at (datetime | None)
        """
        return {
            "user_id": self.user_id,
            "strength": self.strength,
            "endurance": self.endurance,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "experience_points": self.experience_points,
            "level": self.level,
            "stat_total": self.get_stat_total(),
            "stat_average": self.get_stat_average(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class LifeStat:
    """Pure domain entity for life tracking stats."""

    user_id: int
    category: str
    name: str
    value: Decimal = Decimal("0")
    target: Decimal | None = None
    unit: str = ""
    notes: str = ""

    # Metadata
    last_updated: datetime | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        """
        Post-initialization: normalize and validate category and numeric values.

        Calls _validate_category() to enforce and normalize the category to one of
        "health", "wealth", or "relationships" (stored lowercase), and calls
        _validate_value() to ensure `value` (and `target` when present) are numeric
        and converted to Decimal.
        """
        self._validate_category()
        self._validate_value()

    def _validate_category(self):
        """
        Validate that the instance's category is one of the allowed values and normalize it to lowercase.

        Checks that `self.category` (case-insensitive) is one of: "health", "wealth", or "relationships".
        On success, stores the normalized lowercase category back to `self.category`.
        Raises:
            ValueError: If `self.category` is not one of the allowed values.
        """
        valid_categories = ["health", "wealth", "relationships"]
        if self.category.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        self.category = self.category.lower()

    def _validate_value(self):
        """
        Validate and normalize the LifeStat value and optional target.

        Ensures `value` is numeric (int, float, or Decimal) and converts int/float inputs to Decimal (using string conversion to preserve precision). If `target` is provided, performs the same validation and conversion. Raises ValueError if either `value` or `target` is not a numeric type.
        """
        if not isinstance(self.value, (int, float, Decimal)):
            raise ValueError("Value must be a number")

        if isinstance(self.value, (int, float)):
            self.value = Decimal(str(self.value))

        if self.target is not None:
            if not isinstance(self.target, (int, float, Decimal)):
                raise ValueError("Target must be a number")
            if isinstance(self.target, (int, float)):
                self.target = Decimal(str(self.target))

    def update_value(self, new_value: Decimal, notes: str = "") -> Decimal:
        """
        Update the stat's value.

        Accepts a Decimal or a numeric type (int/float — converted to Decimal), sets the new value, replaces notes if provided, updates last_updated to the current UTC time, and returns the stored Decimal value.

        Parameters:
            new_value: New value for the stat; ints and floats will be converted to Decimal.
            notes: Optional notes to replace the existing notes.

        Returns:
            Decimal: The updated value stored on the instance.
        """
        if isinstance(new_value, (int, float)):
            new_value = Decimal(str(new_value))

        self.value = new_value
        if notes:
            self.notes = notes
        self.last_updated = datetime.utcnow()

        return self.value

    def set_target(self, target_value: Decimal | None) -> None:
        """
        Set or clear the target value for this LifeStat.

        If a numeric (int or float) is provided, it is converted to Decimal. Passing None clears the target. Updates the instance's `target` and sets `last_updated` to the current UTC time.
        """
        if target_value is not None:
            if isinstance(target_value, (int, float)):
                target_value = Decimal(str(target_value))

        self.target = target_value
        self.last_updated = datetime.utcnow()

    def progress_percentage(self) -> float:
        """
        Return the current value as a percentage of the target.

        Returns 0.0 if no target is set or the target is zero. Otherwise returns (value / target) * 100 capped at 100.0 and rounded to 2 decimal places.
        """
        if self.target is None or self.target == 0:
            return 0.0

        progress = min(100.0, float((self.value / self.target) * 100))
        return round(progress, 2)

    def is_target_achieved(self) -> bool:
        """
        Return True if a target is set and the current value is greater than or equal to the target.

        Returns:
            bool: True when `target` is not None and `value >= target`; False if no target is set or the value is below the target.
        """
        if self.target is None:
            return False
        return self.value >= self.target

    def distance_to_target(self) -> Decimal | None:
        """
        Return the non-negative distance remaining to the target or None if no target is set.

        Returns:
            Optional[Decimal]: None when `target` is not provided; otherwise the non-negative `target - value` as a Decimal (returns 0 if the target has been met or exceeded).
        """
        if self.target is None:
            return None
        return max(Decimal("0"), self.target - self.value)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the LifeStat suitable for serialization.

        The returned dict contains primitive types (floats, strings, booleans, datetimes) and derived fields:
        - value and target are converted to floats (target is None if unset).
        - progress_percentage: percentage toward target (0.0 if no target).
        - is_target_achieved: True when value >= target and target is set.
        - distance_to_target: non-negative float distance or None if no target.
        Includes timestamps last_updated and created_at unchanged.
        """
        distance = self.distance_to_target()
        return {
            "user_id": self.user_id,
            "category": self.category,
            "name": self.name,
            "value": float(self.value),
            "target": float(self.target) if self.target else None,
            "unit": self.unit,
            "notes": self.notes,
            "progress_percentage": self.progress_percentage(),
            "is_target_achieved": self.is_target_achieved(),
            "distance_to_target": float(distance) if distance is not None else None,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
        }


@dataclass
class StatHistory:
    """Domain entity for tracking stat changes over time."""

    user_id: int
    stat_type: str  # 'core' or 'life'
    stat_name: str
    old_value: Decimal
    new_value: Decimal
    change_amount: Decimal = field(default=Decimal("0"))
    change_reason: str = ""
    timestamp: datetime | None = None

    def __post_init__(self):
        """
        Post-initialization: ensure timestamp and numeric fields are normalized and compute change_amount.

        If `timestamp` is None, set it to the current UTC time. Convert `old_value` and `new_value` from int/float to Decimal (preserving numeric representation) and then set `change_amount` to `new_value - old_value`. This mutates the instance fields.
        """
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

        # Ensure values are Decimal
        if isinstance(self.old_value, (int, float)):
            self.old_value = Decimal(str(self.old_value))
        if isinstance(self.new_value, (int, float)):
            self.new_value = Decimal(str(self.new_value))

        self.change_amount = self.new_value - self.old_value

    @property
    def is_increase(self) -> bool:
        """Check if this represents an increase."""
        return self.change_amount > 0

    @property
    def is_decrease(self) -> bool:
        """
        Return True if this history entry represents a decrease (change_amount < 0).

        Zero change is not considered a decrease.
        """
        return self.change_amount < 0

    @property
    def percentage_change(self) -> float | None:
        """
        Return the percentage change from old_value to new_value as a float.

        If old_value is zero, returns None to indicate percentage change is undefined.
        The returned value is (change_amount / old_value) * 100 and may be negative for decreases.
        """
        if self.old_value == 0:
            return None
        return float((self.change_amount / self.old_value) * 100)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable dictionary representation of the StatHistory.

        All Decimal numeric fields are converted to floats for JSON-friendly serialization. The returned dict contains:
        - user_id (int)
        - stat_type (str)
        - stat_name (str)
        - old_value (float)
        - new_value (float)
        - change_amount (float)
        - change_reason (str)
        - is_increase (bool)
        - is_decrease (bool)
        - percentage_change (Optional[float]) — None when percentage cannot be computed
        - timestamp (Optional[datetime])
        """
        return {
            "user_id": self.user_id,
            "stat_type": self.stat_type,
            "stat_name": self.stat_name,
            "old_value": float(self.old_value),
            "new_value": float(self.new_value),
            "change_amount": float(self.change_amount),
            "change_reason": self.change_reason,
            "is_increase": self.is_increase,
            "is_decrease": self.is_decrease,
            "percentage_change": self.percentage_change,
            "timestamp": self.timestamp,
        }
