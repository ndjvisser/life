"""
Stats infrastructure repositories - Django ORM implementations.
"""

from datetime import date
from typing import Any

from django.db.models import Avg, Count, Q

from ..domain.entities import CoreStat, LifeStat, StatHistory
from ..domain.repositories import (
    CoreStatRepository,
    LifeStatRepository,
    StatHistoryRepository,
)
from .models import CoreStatModel, LifeStatModel, StatHistoryModel


class DjangoCoreStatRepository(CoreStatRepository):
    """Django ORM implementation of CoreStatRepository."""

    def _to_domain(self, django_model: CoreStatModel) -> CoreStat:
        """Convert Django model to domain entity."""
        return CoreStat(
            user_id=django_model.user.id,
            strength=django_model.strength,
            endurance=django_model.endurance,
            agility=django_model.agility,
            intelligence=django_model.intelligence,
            wisdom=django_model.wisdom,
            charisma=django_model.charisma,
            experience_points=django_model.experience_points,
            level=django_model.level,
            created_at=django_model.created_at,
            updated_at=django_model.updated_at,
        )

    def _from_domain(
        self, domain_entity: CoreStat, django_model: CoreStatModel | None = None
    ) -> CoreStatModel:
        """
        Convert a CoreStat domain entity into a Django CoreStatModel.

        If an existing CoreStatModel is provided it will be updated; otherwise a new model is instantiated by looking up the Django User with id == domain_entity.user_id. The model's stat fields (strength, endurance, agility, intelligence, wisdom, charisma, experience_points, level) are set from the domain entity and updated_at is copied if present.

        Parameters:
            domain_entity (CoreStat): Domain entity containing stat values and user_id.
            django_model (Optional[CoreStatModel]): Existing model to update; if None a new CoreStatModel is created and associated with the User from domain_entity.user_id.

        Returns:
            CoreStatModel: The created or updated Django model instance (not saved).

        Raises:
            django.contrib.auth.models.User.DoesNotExist: If no User exists with id == domain_entity.user_id when creating a new model.
        """
        if django_model is None:
            from django.contrib.auth.models import User

            user = User.objects.get(id=domain_entity.user_id)
            django_model = CoreStatModel(user=user)

        # Update fields
        django_model.strength = domain_entity.strength
        django_model.endurance = domain_entity.endurance
        django_model.agility = domain_entity.agility
        django_model.intelligence = domain_entity.intelligence
        django_model.wisdom = domain_entity.wisdom
        django_model.charisma = domain_entity.charisma
        django_model.experience_points = domain_entity.experience_points
        django_model.level = domain_entity.level

        if domain_entity.updated_at:
            django_model.updated_at = domain_entity.updated_at

        return django_model

    def get_by_user_id(self, user_id: int) -> CoreStat | None:
        """
        Return the CoreStat for the given user ID, or None if no record exists.

        Parameters:
            user_id (int): ID of the user whose core stats to retrieve.

        Returns:
            Optional[CoreStat]: Domain CoreStat mapped from the Django model, or None when not found.
        """
        try:
            django_model = CoreStatModel.objects.select_related("user").get(
                user_id=user_id
            )
            return self._to_domain(django_model)
        except CoreStatModel.DoesNotExist:
            return None

    def save(self, core_stat: CoreStat) -> CoreStat:
        """
        Update an existing CoreStat record from the given domain entity and return the saved domain representation.

        Given a CoreStat whose user_id identifies an existing database record, update that CoreStatModel with values from the domain entity, persist the changes, and return the updated CoreStat domain object.

        Parameters:
            core_stat (CoreStat): Domain entity containing updated values; its user_id is used to locate the existing record.

        Returns:
            CoreStat: The domain entity representing the persisted state after save.

        Raises:
            ValueError: If no CoreStatModel exists for core_stat.user_id.
        """
        try:
            django_model = CoreStatModel.objects.select_related("user").get(
                user_id=core_stat.user_id
            )
            django_model = self._from_domain(core_stat, django_model)
            django_model.save()
            return self._to_domain(django_model)
        except CoreStatModel.DoesNotExist as err:
            raise ValueError(
                f"Core stats not found for user_id: {core_stat.user_id}"
            ) from err

    def create(self, core_stat: CoreStat) -> CoreStat:
        """
        Create and persist a new CoreStat from a domain entity.

        Converts the provided domain CoreStat into a Django model, saves it to the database,
        and returns the saved entity converted back to the domain CoreStat (including any
        database-assigned fields such as timestamps or IDs).

        Parameters:
            core_stat (CoreStat): Domain CoreStat to create and persist.

        Returns:
            CoreStat: The saved domain CoreStat reflecting persisted state.
        """
        django_model = self._from_domain(core_stat)
        django_model.save()
        return self._to_domain(django_model)

    def exists_by_user_id(self, user_id: int) -> bool:
        """Check if core stats exist for user ID."""
        return CoreStatModel.objects.filter(user_id=user_id).exists()


class DjangoLifeStatRepository(LifeStatRepository):
    """Django ORM implementation of LifeStatRepository."""

    def _to_domain(self, django_model: LifeStatModel) -> LifeStat:
        """
        Create a LifeStat domain entity from a LifeStatModel.

        Maps the model's related user id to user_id and copies fields: category, name, value, target, unit, notes, last_updated, and created_at.
        """
        return LifeStat(
            user_id=django_model.user.id,
            category=django_model.category,
            name=django_model.name,
            value=django_model.value,
            target=django_model.target,
            unit=django_model.unit,
            notes=django_model.notes,
            last_updated=django_model.last_updated,
            created_at=django_model.created_at,
        )

    def _from_domain(
        self, domain_entity: LifeStat, django_model: LifeStatModel | None = None
    ) -> LifeStatModel:
        """
        Convert a LifeStat domain entity into a LifeStatModel suitable for persistence.

        If `django_model` is not provided, the function fetches the User with id `domain_entity.user_id`
        and creates a new LifeStatModel associated with that user. The following domain fields are
        copied to the model: category, name, value, target, unit, and notes. If `domain_entity.last_updated`
        is set, it is applied to the model's `last_updated` field.

        Parameters:
            domain_entity (LifeStat): Domain entity to convert.
            django_model (Optional[LifeStatModel]): Existing model to update; if None a new model is created.

        Returns:
            LifeStatModel: The updated or newly created Django model instance.

        Raises:
            django.contrib.auth.models.User.DoesNotExist: If `django_model` is None and no User exists for `domain_entity.user_id`.
        """
        if django_model is None:
            from django.contrib.auth.models import User

            user = User.objects.get(id=domain_entity.user_id)
            django_model = LifeStatModel(user=user)

        # Update fields
        django_model.category = domain_entity.category
        django_model.name = domain_entity.name
        django_model.value = domain_entity.value
        django_model.target = domain_entity.target
        django_model.unit = domain_entity.unit
        django_model.notes = domain_entity.notes

        if domain_entity.last_updated:
            django_model.last_updated = domain_entity.last_updated

        return django_model

    def get_by_user_and_name(
        self, user_id: int, category: str, name: str
    ) -> LifeStat | None:
        """Get life stat by user ID, category, and name."""
        try:
            django_model = LifeStatModel.objects.select_related("user").get(
                user_id=user_id, category=category, name=name
            )
            return self._to_domain(django_model)
        except LifeStatModel.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: int) -> list[LifeStat]:
        """
        Return all life stats for a user, ordered by category then name.

        Parameters:
            user_id (int): ID of the user whose life stats to retrieve.

        Returns:
            List[LifeStat]: Domain LifeStat objects ordered by category then name. Returns an empty list if the user has no life stats.
        """
        django_models = (
            LifeStatModel.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("category", "name")
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_category(self, user_id: int, category: str) -> list[LifeStat]:
        """
        Return all life stat domain objects for a user in a specific category, ordered by stat name.

        The lookup matches the given category exactly and returns a list of LifeStat domain entities for the specified user.

        Returns:
            List[LifeStat]: LifeStat domain instances for the user and category, ordered by name.
        """
        django_models = (
            LifeStatModel.objects.select_related("user")
            .filter(user_id=user_id, category=category)
            .order_by("name")
        )
        return [self._to_domain(model) for model in django_models]

    def save(self, life_stat: LifeStat) -> LifeStat:
        """
        Update an existing LifeStat record from the provided domain entity and return the saved domain object.

        The function locates the existing LifeStatModel by life_stat.user_id, life_stat.category and life_stat.name, applies fields from the domain entity, saves the model, and returns the resulting domain representation.

        Parameters:
            life_stat (LifeStat): Domain entity containing updated values; must include user_id, category, and name to identify the record.

        Returns:
            LifeStat: The saved domain entity reflecting persisted values.

        Raises:
            ValueError: If no LifeStatModel exists for the given user_id, category, and name.
        """
        try:
            django_model = LifeStatModel.objects.select_related("user").get(
                user_id=life_stat.user_id,
                category=life_stat.category,
                name=life_stat.name,
            )
            django_model = self._from_domain(life_stat, django_model)
            django_model.save()
            return self._to_domain(django_model)
        except LifeStatModel.DoesNotExist as err:
            raise ValueError(
                f"Life stat not found: {life_stat.category}.{life_stat.name}"
            ) from err

    def create(self, life_stat: LifeStat) -> LifeStat:
        """
        Create and persist a new LifeStat domain entity.

        Accepts a LifeStat domain object, creates the corresponding Django model record, and returns the saved LifeStat converted back to the domain representation (including any database-populated fields such as timestamps or generated IDs).
        """
        django_model = self._from_domain(life_stat)
        django_model.save()
        return self._to_domain(django_model)

    def delete(self, user_id: int, category: str, name: str) -> bool:
        """
        Delete the LifeStatModel matching the given user_id, category, and name.

        Attempts to remove the corresponding database record. Returns True if a record was found and deleted; returns False if no matching life stat exists.
        """
        try:
            LifeStatModel.objects.get(
                user_id=user_id, category=category, name=name
            ).delete()
            return True
        except LifeStatModel.DoesNotExist:
            return False

    def get_categories_for_user(self, user_id: int) -> list[str]:
        """
        Return a sorted list of distinct life-stat categories that exist for the given user.

        Parameters:
            user_id (int): ID of the user whose categories to retrieve.

        Returns:
            List[str]: Alphabetically ordered distinct category names; empty list if the user has no life stats.
        """
        return list(
            LifeStatModel.objects.filter(user_id=user_id)
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )


class DjangoStatHistoryRepository(StatHistoryRepository):
    """Django ORM implementation of StatHistoryRepository."""

    def _to_domain(self, django_model: StatHistoryModel) -> StatHistory:
        """
        Convert a StatHistoryModel instance into a StatHistory domain entity.

        Maps the related user id and the model's stat fields (stat_type, stat_name, old_value,
        new_value, change_reason, timestamp) into a StatHistory value object.

        Returns:
            StatHistory: Domain entity representing the given Django model.
        """
        return StatHistory(
            user_id=django_model.user.id,
            stat_type=django_model.stat_type,
            stat_name=django_model.stat_name,
            old_value=django_model.old_value,
            new_value=django_model.new_value,
            change_reason=django_model.change_reason,
            timestamp=django_model.timestamp,
        )

    def _from_domain(self, domain_entity: StatHistory) -> StatHistoryModel:
        """
        Create a StatHistoryModel from a StatHistory domain entity.

        Parameters:
            domain_entity (StatHistory): Domain entity containing stat history data and the user_id to associate.

        Returns:
            StatHistoryModel: Django model instance populated from the domain entity (not saved).

        Raises:
            django.contrib.auth.models.User.DoesNotExist: If no User exists with id == domain_entity.user_id.
        """
        from django.contrib.auth.models import User

        user = User.objects.get(id=domain_entity.user_id)

        return StatHistoryModel(
            user=user,
            stat_type=domain_entity.stat_type,
            stat_name=domain_entity.stat_name,
            old_value=domain_entity.old_value,
            new_value=domain_entity.new_value,
            change_amount=domain_entity.change_amount,
            change_reason=domain_entity.change_reason,
            timestamp=domain_entity.timestamp,
        )

    def create(self, stat_history: StatHistory) -> StatHistory:
        """
        Create and persist a StatHistory record from the given domain entity.

        Converts the provided StatHistory to a Django model, saves it to the database, and returns the persisted StatHistory domain object (including any DB-populated fields such as generated ID or timestamp).

        Parameters:
            stat_history (StatHistory): Domain entity to be persisted.

        Returns:
            StatHistory: The saved domain entity reflecting database-populated fields.
        """
        django_model = self._from_domain(stat_history)
        django_model.save()
        return self._to_domain(django_model)

    def get_by_user_id(self, user_id: int, limit: int = 100) -> list[StatHistory]:
        """
        Return a list of the user's stat history entries ordered newest first.

        Returns up to `limit` entries (default 100) for the given user_id, ordered by descending timestamp.
        An empty list is returned when no entries exist for the user.
        """
        django_models = (
            StatHistoryModel.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-timestamp")[:limit]
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_stat(
        self, user_id: int, stat_type: str, stat_name: str, limit: int = 50
    ) -> list[StatHistory]:
        """Get history for a specific stat."""
        django_models = (
            StatHistoryModel.objects.select_related("user")
            .filter(user_id=user_id, stat_type=stat_type, stat_name=stat_name)
            .order_by("-timestamp")[:limit]
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> list[StatHistory]:
        """
        Return stat history entries for a user between start_date and end_date (inclusive).

        The date comparison uses the timestamp's date component and results are ordered by timestamp descending (newest first).

        Parameters:
            user_id (int): ID of the user whose history to retrieve.
            start_date (date): Inclusive start date.
            end_date (date): Inclusive end date.

        Returns:
            List[StatHistory]: Domain StatHistory instances matching the range, ordered newest first.
        """
        django_models = (
            StatHistoryModel.objects.select_related("user")
            .filter(
                user_id=user_id,
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date,
            )
            .order_by("-timestamp")
        )
        return [self._to_domain(model) for model in django_models]

    def get_summary_stats(self, user_id: int, days: int = 30) -> dict[str, Any]:
        """
        Return summary statistics of stat-history changes for a user over a recent period.

        This computes aggregates over the inclusive date range [today - days, today]:
        - total number of history entries, and counts split by stat_type ("core" and "life").
        - top 5 most frequently changed stat names with their change counts.
        - average change_amount for "core" and "life" entries (may be None if no entries).
        - changes_per_day is total_changes divided by days (rounded to 2 decimals); returns 0 when days <= 0.

        Parameters:
            user_id (int): ID of the user whose history is summarized.
            days (int): Number of days in the period ending today (default 30). The range is inclusive of both endpoints.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - period_days (int)
                - total_changes (int)
                - core_stat_changes (int)
                - life_stat_changes (int)
                - most_active_stats (List[Dict[str, Any]]): list of {"stat_name": str, "change_count": int}
                - average_changes (Dict[str, Optional[float]]): keys "avg_core_change" and "avg_life_change"
                - changes_per_day (float)
        """
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days)

        # Get recent history
        recent_history = StatHistoryModel.objects.filter(
            user_id=user_id,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date,
        )

        # Calculate summary statistics
        total_changes = recent_history.count()
        core_changes = recent_history.filter(stat_type="core").count()
        life_changes = recent_history.filter(stat_type="life").count()

        # Get most active stats
        most_active_stats = list(
            recent_history.values("stat_name")
            .annotate(change_count=Count("id"))
            .order_by("-change_count")[:5]
        )

        # Get average change amounts by stat type
        avg_changes = recent_history.aggregate(
            avg_core_change=Avg("change_amount", filter=Q(stat_type="core")),
            avg_life_change=Avg("change_amount", filter=Q(stat_type="life")),
        )

        return {
            "period_days": days,
            "total_changes": total_changes,
            "core_stat_changes": core_changes,
            "life_stat_changes": life_changes,
            "most_active_stats": most_active_stats,
            "average_changes": avg_changes,
            "changes_per_day": round(total_changes / days, 2) if days > 0 else 0,
        }
