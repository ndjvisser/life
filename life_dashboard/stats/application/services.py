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
        """
        Initialize the StatService.
        
        Stores the provided repositories for core stats and stat history for use by the service.
        """
        self.core_stat_repo = core_stat_repo
        self.history_repo = history_repo

    def get_or_create_core_stats(self, user_id: int) -> CoreStat:
        """
        Return the CoreStat for the given user, creating and persisting a new CoreStat if none exists.
        
        If a CoreStat does not exist for user_id, a new CoreStat is created with created_at and updated_at set to the current UTC time and persisted via the repository.
        
        Returns:
            CoreStat: The existing or newly created CoreStat for the user.
        """
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
        Update a user's core stat, persist the change, and record history if the value changed.
        
        Retrieves or creates the user's CoreStat, updates the named stat to the provided value, saves the CoreStat, and—only if the value changed—creates a StatHistory entry recording the old and new values and the optional reason.
        
        Parameters:
            user_id (int): ID of the user whose stat is updated.
            stat_name (str): Attribute name of the core stat to update.
            value (int): New numeric value to set for the stat.
            reason (str, optional): Short reason or note for the change (recorded in history when a change occurs).
        
        Returns:
            Tuple[CoreStat, bool]: The saved CoreStat instance and a boolean indicating whether the stat value changed.
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
        Add experience points to a user's core stats, persist the updated CoreStat, and record history entries.
        
        This updates the user's experience (and level, if leveled up) using the domain logic on CoreStat, saves the modified CoreStat via the repository, and creates StatHistory records for the experience change and for a level change when one occurs.
        
        Parameters:
            user_id (int): ID of the user whose stats will be updated.
            points (int): Number of experience points to add.
            reason (str): Optional reason stored on the experience history entry; if omitted a default reason is used.
        
        Returns:
            Tuple[CoreStat, bool]: The persisted CoreStat and a boolean indicating whether a level-up occurred.
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
        """
        Return the CoreStat for the given user or None if no core stats exist.
        
        Parameters:
            user_id (int): ID of the user.
        
        Returns:
            Optional[CoreStat]: The user's CoreStat, or None if not found.
        """
        return self.core_stat_repo.get_by_user_id(user_id)

    def get_stat_history(
        self, user_id: int, stat_name: str, limit: int = 50
    ) -> List[StatHistory]:
        """
        Return history entries for a user's core stat.
        
        Retrieves up to `limit` StatHistory records for the given `stat_name` of type "core" for `user_id`.
        Records are returned in descending time order (most recent first).
        
        Parameters:
            user_id (int): ID of the user whose stat history to fetch.
            stat_name (str): Name of the core stat (e.g., "experience", "level").
            limit (int): Maximum number of history records to return (default 50).
        
        Returns:
            List[StatHistory]: A list of StatHistory entries for the requested stat (may be empty).
        """
        return self.history_repo.get_by_stat(user_id, "core", stat_name, limit)


class LifeStatService:
    """Service for life stat management."""

    def __init__(
        self, life_stat_repo: LifeStatRepository, history_repo: StatHistoryRepository
    ):
        """
        Initialize the LifeStatService with repositories.
        
        Stores the life stat repository and the history repository used by the service for persistence and history recording.
        """
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
        Create a new life stat for a user or update an existing one.
        
        If a LifeStat with the given user_id, category, and name exists, updates its value, optional target, unit, and notes; saves the change and records a StatHistory entry only when the value changes. If no existing stat is found, creates and persists a new LifeStat and records a creation StatHistory (old_value = 0).
        
        Parameters:
            user_id (int): ID of the user owning the stat.
            category (str): Stat category (e.g., "health", "wealth", "relationships").
            name (str): Stat name within the category.
            value (Decimal): New stat value.
            target (Optional[Decimal]): Optional target value for the stat.
            unit (str): Unit of measurement for the stat (optional).
            notes (str): Optional notes or reason used for the history entry.
        
        Returns:
            Tuple[LifeStat, bool]: (the saved LifeStat, was_created) where was_created is True when a new stat was created and False when an existing stat was updated.
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
        """
        Update the numeric value of an existing life stat and record history if it changed.
        
        Retrieves the LifeStat for (user_id, category, name); if found, sets the new value and notes,
        persists the updated stat, and creates a StatHistory entry when the value differs from the previous value.
        
        Parameters:
            user_id (int): ID of the user who owns the stat.
            category (str): Life stat category (e.g., "health", "wealth").
            name (str): Name of the stat within the category.
            value (Decimal): New value to assign to the stat.
            notes (str, optional): Optional note or reason stored with the stat and history entry.
        
        Returns:
            Optional[LifeStat]: The saved LifeStat after update, or None if the stat does not exist.
        """
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
        """
        Set or clear the target value for an existing life stat and persist the change.
        
        If the stat identified by (user_id, category, name) does not exist, returns None.
        Passing None for `target` clears the stat's target. Returns the saved LifeStat instance.
        """
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
        """
        Return a per-category summary of the user's life stats.
        
        The returned dictionary has the following structure:
        {
            "health": [<stat dict>, ...],
            "wealth": [<stat dict>, ...],
            "relationships": [<stat dict>, ...],
            "totals": {
                "health": {"count": int, "targets_achieved": int},
                "wealth": {"count": int, "targets_achieved": int},
                "relationships": {"count": int, "targets_achieved": int},
            },
        }
        
        - Each stat dict is produced by LifeStat.to_dict().
        - "count" is the number of stats in that category.
        - "targets_achieved" is the number of stats in the category for which is_target_achieved() returned True.
        """
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
        """
        Delete a life stat for a user.
        
        Deletes the life stat identified by (category, name) for the given user.
        
        Returns:
            bool: True if a stat was deleted, False if no matching stat existed.
        """
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
        """
        Initialize the service.
        
        Stores the provided StatHistoryRepository for fetching and analyzing historical stat records.
        """
        self.history_repo = history_repo

    def get_recent_activity(self, user_id: int, days: int = 7) -> List[StatHistory]:
        """
        Return recent stat history entries for a user within a date window ending today.
        
        The window covers from (today - days) up to and including today. `days` defaults to 7.
        
        Parameters:
            days (int): Number of days before today to include in the window (inclusive). Defaults to 7.
        
        Returns:
            List[StatHistory]: History records for the user in the specified date range.
        """
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days)
        return self.history_repo.get_by_date_range(user_id, start_date, end_date)

    def get_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Return aggregated activity metrics for a user over a recent time window.
        
        Delegates to the history repository to compute summary statistics for the user's stat activity over the past `days` (inclusive). Typical contents include totals and breakdowns (for example, counts or aggregates per stat or stat type) and the time window covered.
        
        Parameters:
            days (int): Number of days in the lookback window (default 30, inclusive of today).
        
        Returns:
            Dict[str, Any]: A dictionary of aggregated activity metrics as produced by the history repository.
        """
        return self.history_repo.get_summary_stats(user_id, days)

    def detect_trends(
        self, user_id: int, stat_type: str, stat_name: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect a simple trend for a given stat based on recent history.
        
        Performs a lightweight heuristic over up to 100 history records (uses the first 10 most recent changes)
        to classify the stat as "increasing", "decreasing", "stable", or "insufficient_data". Confidence is a
        basic score derived from the proportion of consistent directional changes; it is not a statistical
        measure and should be treated as an approximate indicator.
        
        Parameters:
            user_id (int): ID of the user whose stat history will be analyzed.
            stat_type (str): Type/category of the stat (e.g., "core" or "life"); used to scope the history query.
            stat_name (str): Name of the stat to analyze.
            days (int): Historical window in days to consider (unused by the heuristic if the repository ignores it),
                default 30.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - "trend" (str): One of "increasing", "decreasing", "stable", or "insufficient_data".
                - "confidence" (float): Rounded [0.0, 1.0] score representing heuristic confidence.
                - "recent_changes" (int): Number of recent change records considered.
                - "positive_changes" (int): Count of positive change events in the sample.
                - "negative_changes" (int): Count of negative change events in the sample.
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
