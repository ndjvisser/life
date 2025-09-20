"""
Stats infrastructure repositories - Django ORM implementations.
"""
from datetime import date
from typing import Any, Dict, List, Optional

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
        self, domain_entity: CoreStat, django_model: Optional[CoreStatModel] = None
    ) -> CoreStatModel:
        """Convert domain entity to Django model."""
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

    def get_by_user_id(self, user_id: int) -> Optional[CoreStat]:
        """Get core stats by user ID."""
        try:
            django_model = CoreStatModel.objects.select_related("user").get(
                user_id=user_id
            )
            return self._to_domain(django_model)
        except CoreStatModel.DoesNotExist:
            return None

    def save(self, core_stat: CoreStat) -> CoreStat:
        """Save core stats and return updated entity."""
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
        """Create new core stats."""
        django_model = self._from_domain(core_stat)
        django_model.save()
        return self._to_domain(django_model)

    def exists_by_user_id(self, user_id: int) -> bool:
        """Check if core stats exist for user ID."""
        return CoreStatModel.objects.filter(user_id=user_id).exists()


class DjangoLifeStatRepository(LifeStatRepository):
    """Django ORM implementation of LifeStatRepository."""

    def _to_domain(self, django_model: LifeStatModel) -> LifeStat:
        """Convert Django model to domain entity."""
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
        self, domain_entity: LifeStat, django_model: Optional[LifeStatModel] = None
    ) -> LifeStatModel:
        """Convert domain entity to Django model."""
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
    ) -> Optional[LifeStat]:
        """Get life stat by user ID, category, and name."""
        try:
            django_model = LifeStatModel.objects.select_related("user").get(
                user_id=user_id, category=category, name=name
            )
            return self._to_domain(django_model)
        except LifeStatModel.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: int) -> List[LifeStat]:
        """Get all life stats for a user."""
        django_models = (
            LifeStatModel.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("category", "name")
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_category(self, user_id: int, category: str) -> List[LifeStat]:
        """Get life stats by user ID and category."""
        django_models = (
            LifeStatModel.objects.select_related("user")
            .filter(user_id=user_id, category=category)
            .order_by("name")
        )
        return [self._to_domain(model) for model in django_models]

    def save(self, life_stat: LifeStat) -> LifeStat:
        """Save life stat and return updated entity."""
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
        """Create new life stat."""
        django_model = self._from_domain(life_stat)
        django_model.save()
        return self._to_domain(django_model)

    def delete(self, user_id: int, category: str, name: str) -> bool:
        """Delete life stat."""
        try:
            LifeStatModel.objects.get(
                user_id=user_id, category=category, name=name
            ).delete()
            return True
        except LifeStatModel.DoesNotExist:
            return False

    def get_categories_for_user(self, user_id: int) -> List[str]:
        """Get all categories that have stats for a user."""
        return list(
            LifeStatModel.objects.filter(user_id=user_id)
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )


class DjangoStatHistoryRepository(StatHistoryRepository):
    """Django ORM implementation of StatHistoryRepository."""

    def _to_domain(self, django_model: StatHistoryModel) -> StatHistory:
        """Convert Django model to domain entity."""
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
        """Convert domain entity to Django model."""
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
        """Create new stat history entry."""
        django_model = self._from_domain(stat_history)
        django_model.save()
        return self._to_domain(django_model)

    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[StatHistory]:
        """Get stat history for user, most recent first."""
        django_models = (
            StatHistoryModel.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-timestamp")[:limit]
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_stat(
        self, user_id: int, stat_type: str, stat_name: str, limit: int = 50
    ) -> List[StatHistory]:
        """Get history for a specific stat."""
        django_models = (
            StatHistoryModel.objects.select_related("user")
            .filter(user_id=user_id, stat_type=stat_type, stat_name=stat_name)
            .order_by("-timestamp")[:limit]
        )
        return [self._to_domain(model) for model in django_models]

    def get_by_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> List[StatHistory]:
        """Get stat history within date range."""
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

    def get_summary_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for recent period."""
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
