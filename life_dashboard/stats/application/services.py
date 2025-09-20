"""
Stats application services - use case orchestration and business workflows.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from ..domain.entities import CoreStat, LifeStat, StatHistory
from ..domain.repositories import (
    CoreStatRepository,
    LifeStatRepository,
    StatHistoryRepository,
)


class StatService:
    """Service for core stat management."""

    def __init__(
        self, core_stat_repo: CoreStatRepository, history_repo: StatHistoryRepository
    ):
        self.core_stat_repo = core_stat_repo
        self.history_repo = history_repo

    def get_or_create_core_stats(self, user_id: int) -> CoreStat:
        """Get existing core stats or create new ones."""
        core_stats = self.core_stat_repo.get_by_user_id(user_id)
        if not core_stats:
            core_stats = CoreStat(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            core_stats = self.core_stat_repo.create(core_stats)

        return core_stats

    def update_stat(
        self, user_id: int, stat_name: str, value: int, reason: str = ""
    ) -> Tuple[CoreStat, bool]:
        """
        Update a core stat value.

        Args:
            user_id: User ID
            stat_name: Name of the stat to update
            value: New value for the stat
            reason: Reason for the change

        Returns:
            tuple: (updated_core_stats, value_changed)
        """
        core_stats = self.get_or_create_core_stats(user_id)
        old_value = getattr(core_stats, stat_name, 0)

        # Update the stat
        new_value = core_stats.update_stat(stat_name, value)

        # Save the updated stats
        updated_stats = self.core_stat_repo.save(core_stats)

        # Record history if value changed
        value_changed = old_value != new_value
        if value_changed:
            history = StatHistory(
                user_id=user_id,
                stat_type="core",
                stat_name=stat_name,
                old_value=Decimal(str(old_value)),
                new_value=Decimal(str(new_value)),
                change_reason=reason,
            )
            self.history_repo.create(history)

        return updated_stats, value_changed

    def add_experience(
        self, user_id: int, points: int, reason: str = ""
    ) -> Tuple[CoreStat, bool]:
        """
        Add experience points to core stats.

        Args:
            user_id: User ID
            points: Experience points to add
            reason: Reason for the experience gain

        Returns:
            tuple: (updated_core_stats, level_up_occurred)
        """
        core_stats = self.get_or_create_core_stats(user_id)
        old_level = core_stats.level
        old_experience = core_stats.experience_points

        # Add experience using domain logic
        new_level, level_up_occurred = core_stats.add_experience(points)

        # Save updated stats
        updated_stats = self.core_stat_repo.save(core_stats)

        # Record experience history
        history = StatHistory(
            user_id=user_id,
            stat_type="core",
            stat_name="experience_points",
            old_value=Decimal(str(old_experience)),
            new_value=Decimal(str(updated_stats.experience_points)),
            change_reason=reason or f"Experience gained: {points} points",
        )
        self.history_repo.create(history)

        # Record level change if it occurred
        if level_up_occurred:
            level_history = StatHistory(
                user_id=user_id,
                stat_type="core",
                stat_name="level",
                old_value=Decimal(str(old_level)),
                new_value=Decimal(str(new_level)),
                change_reason="Level up from experience gain",
            )
            self.history_repo.create(level_history)

        return updated_stats, level_up_occurred

    def get_core_stats(self, user_id: int) -> Optional[CoreStat]:
        """Get core stats for user."""
        return self.core_stat_repo.get_by_user_id(user_id)

    def get_stat_history(
        self, user_id: int, stat_name: str, limit: int = 50
    ) -> List[StatHistory]:
        """Get history for a specific core stat."""
        return self.history_repo.get_by_stat(user_id, "core", stat_name, limit)


class LifeStatService:
    """Service for life stat management."""

    def __init__(
        self, life_stat_repo: LifeStatRepository, history_repo: StatHistoryRepository
    ):
        self.life_stat_repo = life_stat_repo
        self.history_repo = history_repo

    def create_or_update_stat(
        self,
        user_id: int,
        category: str,
        name: str,
        value: Decimal,
        target: Optional[Decimal] = None,
        unit: str = "",
        notes: str = "",
    ) -> Tuple[LifeStat, bool]:
        """
        Create or update a life stat.

        Args:
            user_id: User ID
            category: Stat category (health, wealth, relationships)
            name: Stat name
            value: Stat value
            target: Optional target value
            unit: Unit of measurement
            notes: Optional notes

        Returns:
            tuple: (life_stat, was_created)
        """
        existing_stat = self.life_stat_repo.get_by_user_and_name(
            user_id, category, name
        )

        if existing_stat:
            # Update existing stat
            old_value = existing_stat.value
            existing_stat.update_value(value, notes)
            if target is not None:
                existing_stat.set_target(target)
            if unit:
                existing_stat.unit = unit

            updated_stat = self.life_stat_repo.save(existing_stat)

            # Record history if value changed
            if old_value != value:
                history = StatHistory(
                    user_id=user_id,
                    stat_type="life",
                    stat_name=f"{category}.{name}",
                    old_value=old_value,
                    new_value=value,
                    change_reason=notes or "Stat updated",
                )
                self.history_repo.create(history)

            return updated_stat, False
        else:
            # Create new stat
            new_stat = LifeStat(
                user_id=user_id,
                category=category,
                name=name,
                value=value,
                target=target,
                unit=unit,
                notes=notes,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
            )

            created_stat = self.life_stat_repo.create(new_stat)

            # Record creation history
            history = StatHistory(
                user_id=user_id,
                stat_type="life",
                stat_name=f"{category}.{name}",
                old_value=Decimal("0"),
                new_value=value,
                change_reason=notes or "Stat created",
            )
            self.history_repo.create(history)

            return created_stat, True

    def update_stat_value(
        self, user_id: int, category: str, name: str, value: Decimal, notes: str = ""
    ) -> Optional[LifeStat]:
        """Update just the value of an existing life stat."""
        stat = self.life_stat_repo.get_by_user_and_name(user_id, category, name)
        if not stat:
            return None

        old_value = stat.value
        stat.update_value(value, notes)
        updated_stat = self.life_stat_repo.save(stat)

        # Record history
        if old_value != value:
            history = StatHistory(
                user_id=user_id,
                stat_type="life",
                stat_name=f"{category}.{name}",
                old_value=old_value,
                new_value=value,
                change_reason=notes or "Value updated",
            )
            self.history_repo.create(history)

        return updated_stat

    def set_stat_target(
        self, user_id: int, category: str, name: str, target: Optional[Decimal]
    ) -> Optional[LifeStat]:
        """Set target for an existing life stat."""
        stat = self.life_stat_repo.get_by_user_and_name(user_id, category, name)
        if not stat:
            return None

        stat.set_target(target)
        return self.life_stat_repo.save(stat)

    def get_stats_by_category(self, user_id: int, category: str) -> List[LifeStat]:
        """Get all life stats for a user in a specific category."""
        return self.life_stat_repo.get_by_category(user_id, category)

    def get_all_stats(self, user_id: int) -> List[LifeStat]:
        """Get all life stats for a user."""
        return self.life_stat_repo.get_by_user_id(user_id)

    def get_stats_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of all life stats by category."""
        all_stats = self.get_all_stats(user_id)

        summary = {
            "health": [],
            "wealth": [],
            "relationships": [],
            "totals": {
                "health": {"count": 0, "targets_achieved": 0},
                "wealth": {"count": 0, "targets_achieved": 0},
                "relationships": {"count": 0, "targets_achieved": 0},
            },
        }

        for stat in all_stats:
            category_stats = summary[stat.category]
            category_stats.append(stat.to_dict())

            # Update totals
            summary["totals"][stat.category]["count"] += 1
            if stat.is_target_achieved():
                summary["totals"][stat.category]["targets_achieved"] += 1

        return summary

    def delete_stat(self, user_id: int, category: str, name: str) -> bool:
        """Delete a life stat."""
        return self.life_stat_repo.delete(user_id, category, name)

    def get_stat_history(
        self, user_id: int, category: str, name: str, limit: int = 50
    ) -> List[StatHistory]:
        """Get history for a specific life stat."""
        stat_name = f"{category}.{name}"
        return self.history_repo.get_by_stat(user_id, "life", stat_name, limit)


class StatAnalyticsService:
    """Service for stat analytics and insights."""

    def __init__(self, history_repo: StatHistoryRepository):
        self.history_repo = history_repo

    def get_recent_activity(self, user_id: int, days: int = 7) -> List[StatHistory]:
        """Get recent stat activity for user."""
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days)
        return self.history_repo.get_by_date_range(user_id, start_date, end_date)

    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get summary of stat activity."""
        return self.history_repo.get_summary_stats(user_id, days)

    def detect_trends(
        self, user_id: int, stat_type: str, stat_name: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect trends in stat changes.

        This is a simplified implementation - in a real system you'd use
        more sophisticated statistical analysis.
        """
        history = self.history_repo.get_by_stat(
            user_id, stat_type, stat_name, limit=100
        )

        if len(history) < 2:
            return {"trend": "insufficient_data", "confidence": 0.0}

        # Simple trend detection based on recent changes
        recent_changes = [h.change_amount for h in history[:10]]
        positive_changes = sum(1 for change in recent_changes if change > 0)
        negative_changes = sum(1 for change in recent_changes if change < 0)

        if positive_changes > negative_changes * 1.5:
            trend = "increasing"
            confidence = positive_changes / len(recent_changes)
        elif negative_changes > positive_changes * 1.5:
            trend = "decreasing"
            confidence = negative_changes / len(recent_changes)
        else:
            trend = "stable"
            confidence = 0.5

        return {
            "trend": trend,
            "confidence": round(confidence, 2),
            "recent_changes": len(recent_changes),
            "positive_changes": positive_changes,
            "negative_changes": negative_changes,
        }
