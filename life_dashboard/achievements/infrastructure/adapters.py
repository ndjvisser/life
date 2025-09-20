"""
Infrastructure adapters for achievements context.
Handles mapping between domain entities and Django models.
"""

from life_dashboard.achievements.domain.entities import Achievement as DomainAchievement
from life_dashboard.achievements.domain.entities import AchievementTier
from life_dashboard.achievements.domain.entities import (
    UserAchievement as DomainUserAchievement,
)
from life_dashboard.achievements.models import Achievement as DjangoAchievement
from life_dashboard.achievements.models import UserAchievement as DjangoUserAchievement


class AchievementAdapter:
    """Adapter for mapping between domain Achievement entities and Django models."""

    @staticmethod
    def domain_tier_to_db_tier(domain_tier: AchievementTier) -> str:
        """Convert domain tier enum to database tier string."""
        return domain_tier.value.upper()

    @staticmethod
    def db_tier_to_domain_tier(db_tier: str) -> AchievementTier:
        """Convert database tier string to domain tier enum."""
        return AchievementTier(db_tier.lower())

    @staticmethod
    def domain_to_django(domain_achievement: DomainAchievement) -> DjangoAchievement:
        """Convert domain Achievement entity to Django model."""
        return DjangoAchievement(
            name=domain_achievement.name,
            description=domain_achievement.description,
            tier=AchievementAdapter.domain_tier_to_db_tier(domain_achievement.tier),
            icon=domain_achievement.icon,
            experience_reward=domain_achievement.experience_reward,
            required_level=domain_achievement.required_level,
            required_skill_level=domain_achievement.required_skill_level,
            required_quest_completions=domain_achievement.required_quest_completions,
        )

    @staticmethod
    def django_to_domain(django_achievement: DjangoAchievement) -> DomainAchievement:
        """Convert Django model to domain Achievement entity."""
        return DomainAchievement(
            achievement_id=str(django_achievement.id)
            if django_achievement.id
            else None,
            name=django_achievement.name,
            description=django_achievement.description,
            tier=AchievementAdapter.db_tier_to_domain_tier(django_achievement.tier),
            icon=django_achievement.icon,
            experience_reward=django_achievement.experience_reward,
            required_level=django_achievement.required_level,
            required_skill_level=django_achievement.required_skill_level,
            required_quest_completions=django_achievement.required_quest_completions,
        )


class UserAchievementAdapter:
    """Adapter for mapping between domain UserAchievement entities and Django models."""

    @staticmethod
    def domain_to_django(
        domain_user_achievement: DomainUserAchievement,
        django_achievement: DjangoAchievement,
        user_id: int,
    ) -> DjangoUserAchievement:
        """Convert domain UserAchievement entity to Django model."""
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        django_user_achievement = DjangoUserAchievement(
            user=user,
            achievement=django_achievement,
            notes=domain_user_achievement.notes,
        )

        # Set unlocked_at if the domain entity is unlocked
        if domain_user_achievement.unlocked_at:
            django_user_achievement.unlocked_at = domain_user_achievement.unlocked_at

        return django_user_achievement

    @staticmethod
    def django_to_domain(
        django_user_achievement: DjangoUserAchievement,
    ) -> DomainUserAchievement:
        """Convert Django model to domain UserAchievement entity."""
        return DomainUserAchievement(
            user_achievement_id=str(django_user_achievement.id)
            if django_user_achievement.id
            else None,
            user_id=django_user_achievement.user.id,
            achievement_id=str(django_user_achievement.achievement.id),
            unlocked_at=django_user_achievement.unlocked_at,
            notes=django_user_achievement.notes,
        )
