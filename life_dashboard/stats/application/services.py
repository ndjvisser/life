"""
Stats application services - use case orchestration and business workflows.
"""

from dataclasses import dataclass
from decimal import Decimal

from django.utils import timezone

from ..domain.entities import CoreStat, LifeStat, StatHistory
from ..domain.repositories import (
    CoreStatRepository,
    LifeStatRepository,
    StatHistoryRepository,
)


class StatService:
    """Service for core stat management."""

    def __init__(
        self,
        core_stat_repo: CoreStatRepository,
        life_stat_repo: LifeStatRepository,
        history_repo: StatHistoryRepository,
    ):
        """
        Initialize the StatService.

        Stores the provided repositories for core stats, life stats, and stat history for use by the service.
        """
        self.core_stat_repo = core_stat_repo
        self.life_stat_repo = life_stat_repo
        self.history_repo = history_repo

    def get_or_create_core_stats(self, user_id: int) -> CoreStat:
        """
        Return the CoreStat for the given user, creating and persisting a new CoreStat if none exists.

        If a CoreStat does not exist for user_id, a new CoreStat is created with
        created_at and updated_at set to the current UTC time and persisted via the repository.

        Returns:
            CoreStat: The existing or newly created CoreStat for the user.
        """
        core_stats = self.core_stat_repo.get_by_user_id(user_id)
        if not core_stats:
            core_stats = CoreStat(
                user_id=user_id,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            self.core_stat_repo.save(core_stats)
        return core_stats

    def update_core_stat(
        self, user_id: int, stat_name: str, new_value: int
    ) -> CoreStat:
        """
        Update a specific core stat for a user and record the change in history.

        Args:
            user_id: The user's ID
            stat_name: Name of the stat to update (e.g., 'strength', 'intelligence')
            new_value: New value for the stat

        Returns:
            CoreStat: The updated core stats entity

        Raises:
            ValueError: If stat_name is invalid or new_value is out of range
        """
        core_stats = self.get_or_create_core_stats(user_id)

        # Get the old value
        old_value = getattr(core_stats, stat_name, None)
        if old_value is None:
            raise ValueError(f"Invalid stat name: {stat_name}")

        # Update the stat
        setattr(core_stats, stat_name, new_value)
        core_stats.updated_at = timezone.now()

        # Save the updated stats
        self.core_stat_repo.save(core_stats)

        # Record the change in history
        history_entry = StatHistory(
            user_id=user_id,
            stat_type="core",
            stat_name=stat_name,
            old_value=Decimal(str(old_value)),
            new_value=Decimal(str(new_value)),
            change_amount=Decimal(str(new_value - old_value)),
            change_reason="Manual update",
            timestamp=timezone.now(),
        )
        self.history_repo.save(history_entry)

        return core_stats

    def add_experience(
        self, user_id: int, experience_points: int, reason: str = "Experience gained"
    ) -> CoreStat:
        """
        Add experience points to a user's core stats and handle level ups.

        Args:
            user_id: The user's ID
            experience_points: Amount of experience to add
            reason: Reason for the experience gain

        Returns:
            CoreStat: The updated core stats entity
        """
        core_stats = self.get_or_create_core_stats(user_id)

        old_experience = core_stats.experience_points
        old_level = core_stats.level

        # Add experience
        core_stats.experience_points += experience_points
        core_stats.updated_at = timezone.now()

        # Recalculate level (this happens in the domain entity)
        core_stats._calculate_level()

        # Save the updated stats
        self.core_stat_repo.save(core_stats)

        # Record experience gain in history
        history_entry = StatHistory(
            user_id=user_id,
            stat_type="core",
            stat_name="experience_points",
            old_value=Decimal(str(old_experience)),
            new_value=Decimal(str(core_stats.experience_points)),
            change_amount=Decimal(str(experience_points)),
            change_reason=reason,
            timestamp=timezone.now(),
        )
        self.history_repo.save(history_entry)

        # Record level up if it occurred
        if core_stats.level > old_level:
            level_history = StatHistory(
                user_id=user_id,
                stat_type="core",
                stat_name="level",
                old_value=Decimal(str(old_level)),
                new_value=Decimal(str(core_stats.level)),
                change_amount=Decimal(str(core_stats.level - old_level)),
                change_reason=f"Level up from experience gain: {reason}",
                timestamp=timezone.now(),
            )
            self.history_repo.save(level_history)

        return core_stats

    def get_recent_activity(self, user_id: int, days: int = 7) -> list[StatHistory]:
        """
        Get recent stat changes for a user.

        Args:
            user_id: The user's ID
            days: Number of days to look back

        Returns:
            List[StatHistory]: Recent stat changes
        """
        return self.history_repo.get_recent_for_user(user_id, days)


class LifeStatService:
    """Service for life stat management."""

    def __init__(
        self, life_stat_repo: LifeStatRepository, history_repo: StatHistoryRepository
    ):
        """Initialize the LifeStatService."""
        self.life_stat_repo = life_stat_repo
        self.history_repo = history_repo

    def update_life_stat(
        self,
        user_id: int,
        category: str,
        subcategory: str,
        new_value: Decimal,
        unit: str = "",
        notes: str = "",
    ) -> LifeStat:
        """
        Update or create a life stat for a user.

        Args:
            user_id: The user's ID
            category: Main category (e.g., 'health', 'wealth', 'relationships')
            subcategory: Subcategory (e.g., 'physical', 'mental')
            new_value: New value for the stat
            unit: Unit of measurement
            notes: Optional notes

        Returns:
            LifeStat: The updated or created life stat
        """
        # Try to get existing stat
        life_stat = self.life_stat_repo.get_by_user_and_category(
            user_id, category, subcategory
        )

        old_value = Decimal("0")
        if life_stat:
            old_value = life_stat.current_value
            life_stat.current_value = new_value
            life_stat.unit = unit
            life_stat.notes = notes
            life_stat.last_updated = timezone.now()
        else:
            life_stat = LifeStat(
                user_id=user_id,
                category=category,
                subcategory=subcategory,
                current_value=new_value,
                unit=unit,
                notes=notes,
                last_updated=timezone.now(),
                created_at=timezone.now(),
            )

        # Save the stat
        self.life_stat_repo.save(life_stat)

        # Record the change in history
        history_entry = StatHistory(
            user_id=user_id,
            stat_type="life",
            stat_name=f"{category}.{subcategory}",
            old_value=old_value,
            new_value=new_value,
            change_amount=new_value - old_value,
            change_reason="Life stat update",
            timestamp=timezone.now(),
        )
        self.history_repo.save(history_entry)

        return life_stat

    def get_user_life_stats(self, user_id: int) -> list[LifeStat]:
        """Get all life stats for a user."""
        return self.life_stat_repo.get_by_user_id(user_id)

    def get_life_stats_by_category(self, user_id: int, category: str) -> list[LifeStat]:
        """Get life stats for a user in a specific category."""
        return self.life_stat_repo.get_by_user_and_main_category(user_id, category)


@dataclass(frozen=True)
class StatChangeSummary:
    """Aggregated view of a user's recent stat history."""

    user_id: int
    total_entries: int
    total_increase: Decimal
    total_decrease: Decimal

    @property
    def net_change(self) -> Decimal:
        """Return the net change across all history entries."""

        return self.total_increase + self.total_decrease


class StatAnalyticsService:
    """High-level analytics derived from stat history entries."""

    def __init__(self, history_repo: StatHistoryRepository):
        self.history_repo = history_repo

    def summarize_recent_changes(
        self, user_id: int, limit: int = 100
    ) -> StatChangeSummary:
        """Summarize the recent stat history for a user."""

        history_entries = self.history_repo.get_by_user_id(user_id, limit=limit)

        total_increase = Decimal("0")
        total_decrease = Decimal("0")

        for entry in history_entries:
            if entry.change_amount >= 0:
                total_increase += entry.change_amount
            else:
                total_decrease += entry.change_amount

        return StatChangeSummary(
            user_id=user_id,
            total_entries=len(history_entries),
            total_increase=total_increase,
            total_decrease=total_decrease,
        )
