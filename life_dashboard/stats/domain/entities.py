"""
Stats domain entities - pure Python business logic without Django dependencies.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate stats on creation."""
        self._validate_stats()
        self._calculate_level()

    def _validate_stats(self):
        """Validate all stat values are within acceptable range."""
        stat_fields = [
            "strength",
            "endurance",
            "agility",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        for field in stat_fields:
            value = getattr(self, field)
            if not isinstance(value, int) or value < 1 or value > 100:
                raise ValueError(f"{field} must be an integer between 1 and 100")

    def _calculate_level(self):
        """Calculate level based on experience points."""
        self.level = max(1, (self.experience_points // 1000) + 1)

    def update_stat(self, stat_name: str, value: int) -> int:
        """
        Update a specific stat value.

        Args:
            stat_name: Name of the stat to update
            value: New value for the stat

        Returns:
            The new stat value

        Raises:
            ValueError: If stat name is invalid or value is out of range
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

    def add_experience(self, points: int) -> Tuple[int, bool]:
        """
        Add experience points and calculate level.

        Args:
            points: Experience points to add

        Returns:
            tuple: (new_level, level_up_occurred)
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
        """Get total of all core stats."""
        return (
            self.strength
            + self.endurance
            + self.agility
            + self.intelligence
            + self.wisdom
            + self.charisma
        )

    def get_stat_average(self) -> float:
        """Get average of all core stats."""
        return self.get_stat_total() / 6

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
    target: Optional[Decimal] = None
    unit: str = ""
    notes: str = ""

    # Metadata
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate life stat on creation."""
        self._validate_category()
        self._validate_value()

    def _validate_category(self):
        """Validate category is one of the allowed values."""
        valid_categories = ["health", "wealth", "relationships"]
        if self.category.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        self.category = self.category.lower()

    def _validate_value(self):
        """Validate stat value."""
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
        Update the stat value.

        Args:
            new_value: New value for the stat
            notes: Optional notes about the update

        Returns:
            The new value
        """
        if isinstance(new_value, (int, float)):
            new_value = Decimal(str(new_value))

        self.value = new_value
        if notes:
            self.notes = notes
        self.last_updated = datetime.utcnow()

        return self.value

    def set_target(self, target_value: Optional[Decimal]) -> None:
        """Set target value for this stat."""
        if target_value is not None:
            if isinstance(target_value, (int, float)):
                target_value = Decimal(str(target_value))

        self.target = target_value
        self.last_updated = datetime.utcnow()

    def progress_percentage(self) -> float:
        """Calculate progress towards target as percentage."""
        if self.target is None or self.target == 0:
            return 0.0

        progress = min(100.0, float((self.value / self.target) * 100))
        return round(progress, 2)

    def is_target_achieved(self) -> bool:
        """Check if target has been achieved."""
        if self.target is None:
            return False
        return self.value >= self.target

    def distance_to_target(self) -> Optional[Decimal]:
        """Calculate distance to target."""
        if self.target is None:
            return None
        return max(Decimal("0"), self.target - self.value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
    change_amount: Decimal
    change_reason: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Calculate change amount and set timestamp."""
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
        """Check if this represents a decrease."""
        return self.change_amount < 0

    @property
    def percentage_change(self) -> Optional[float]:
        """Calculate percentage change."""
        if self.old_value == 0:
            return None
        return float((self.change_amount / self.old_value) * 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
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
