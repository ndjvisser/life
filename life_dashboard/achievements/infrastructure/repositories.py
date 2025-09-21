"""Django-backed repository implementations for achievements domain."""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from life_dashboard.achievements.domain.entities import AchievementTier
from life_dashboard.achievements.domain.entities import (
    UserAchievement as DomainUserAchievement,
)
from life_dashboard.achievements.domain.repositories import UserAchievementRepository
from life_dashboard.achievements.domain.value_objects import (
    AchievementId,
    UserAchievementId,
)
from life_dashboard.achievements.models import UserAchievement as DjangoUserAchievement
from life_dashboard.common.value_objects import UserId


class DjangoUserAchievementRepository(UserAchievementRepository):
    """Persistence adapter for :class:`UserAchievement` entities."""

    def save(self, user_achievement: DomainUserAchievement) -> DomainUserAchievement:
        """Persist a user achievement, handling duplicate unlocks safely."""

        user_id = self._coerce_user_id(user_achievement.user_id)
        achievement_id = self._coerce_achievement_id(user_achievement.achievement_id)

        with transaction.atomic():
            try:
                with transaction.atomic():
                    django_user_achievement = DjangoUserAchievement.objects.create(
                        user_id=user_id,
                        achievement_id=achievement_id,
                        notes=user_achievement.notes,
                        unlocked_at=user_achievement.unlocked_at,
                    )
            except IntegrityError:
                existing = DjangoUserAchievement.objects.select_related(
                    "achievement"
                ).get(user_id=user_id, achievement_id=achievement_id)
                return self._map_to_domain(
                    existing, unlock_context=user_achievement.unlock_context
                )

        return self._map_to_domain(
            django_user_achievement, unlock_context=user_achievement.unlock_context
        )

    def get_by_id(
        self, user_achievement_id: UserAchievementId
    ) -> DomainUserAchievement | None:
        try:
            django_user_achievement = DjangoUserAchievement.objects.get(
                id=self._coerce_user_achievement_id(user_achievement_id)
            )
        except DjangoUserAchievement.DoesNotExist:
            return None

        return self._map_to_domain(django_user_achievement)

    def get_user_achievements(self, user_id: UserId) -> list[DomainUserAchievement]:
        queryset = DjangoUserAchievement.objects.filter(
            user_id=self._coerce_user_id(user_id)
        ).order_by("-unlocked_at")
        return [self._map_to_domain(item) for item in queryset]

    def get_user_achievements_by_tier(
        self, user_id: UserId, tier: AchievementTier
    ) -> list[DomainUserAchievement]:
        queryset = DjangoUserAchievement.objects.filter(
            user_id=self._coerce_user_id(user_id),
            achievement__tier=self._coerce_tier(tier),
        ).order_by("-unlocked_at")
        return [self._map_to_domain(item) for item in queryset]

    def get_recent_achievements(
        self, user_id: UserId, days: int = 7
    ) -> list[DomainUserAchievement]:
        cutoff = timezone.now() - timedelta(days=days)
        queryset = DjangoUserAchievement.objects.filter(
            user_id=self._coerce_user_id(user_id),
            unlocked_at__gte=cutoff,
        ).order_by("-unlocked_at")
        return [self._map_to_domain(item) for item in queryset]

    def has_achievement(self, user_id: UserId, achievement_id: AchievementId) -> bool:
        return DjangoUserAchievement.objects.filter(
            user_id=self._coerce_user_id(user_id),
            achievement_id=self._coerce_achievement_id(achievement_id),
        ).exists()

    def get_achievement_count(self, user_id: UserId) -> int:
        return DjangoUserAchievement.objects.filter(
            user_id=self._coerce_user_id(user_id)
        ).count()

    def delete(self, user_achievement_id: UserAchievementId) -> bool:
        deleted, _ = DjangoUserAchievement.objects.filter(
            id=self._coerce_user_achievement_id(user_achievement_id)
        ).delete()
        return deleted > 0

    @staticmethod
    def _map_to_domain(
        django_user_achievement: DjangoUserAchievement,
        *,
        unlock_context: dict[str, Any] | None = None,
    ) -> DomainUserAchievement:
        context = deepcopy(unlock_context) if unlock_context else {}
        return DomainUserAchievement(
            user_id=UserId(django_user_achievement.user_id),
            achievement_id=AchievementId(django_user_achievement.achievement_id),
            unlocked_at=django_user_achievement.unlocked_at,
            notes=django_user_achievement.notes,
            unlock_context=context,
            user_achievement_id=UserAchievementId(django_user_achievement.id)
            if django_user_achievement.id
            else None,
        )

    @staticmethod
    def _coerce_user_id(user_id: UserId | int | str) -> int:
        if isinstance(user_id, UserId):
            return user_id.value
        if isinstance(user_id, str):
            return int(user_id)
        return int(user_id)

    @staticmethod
    def _coerce_achievement_id(achievement_id: AchievementId | int | str) -> int:
        if isinstance(achievement_id, AchievementId):
            return achievement_id.value
        if isinstance(achievement_id, str):
            return int(achievement_id)
        return int(achievement_id)

    @staticmethod
    def _coerce_user_achievement_id(
        user_achievement_id: UserAchievementId | int | str,
    ) -> int:
        if isinstance(user_achievement_id, UserAchievementId):
            return user_achievement_id.value
        if isinstance(user_achievement_id, str):
            return int(user_achievement_id)
        return int(user_achievement_id)

    @staticmethod
    def _coerce_tier(tier: AchievementTier | str) -> str:
        if isinstance(tier, AchievementTier):
            return tier.value
        return str(tier).upper()
