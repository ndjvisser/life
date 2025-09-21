"""Integration tests for achievements infrastructure repositories."""

from datetime import datetime, timezone

import pytest
from django.contrib.auth import get_user_model

from life_dashboard.achievements.domain.entities import (
    UserAchievement as DomainUserAchievement,
)
from life_dashboard.achievements.domain.value_objects import AchievementId
from life_dashboard.achievements.infrastructure.repositories import (
    DjangoUserAchievementRepository,
)
from life_dashboard.achievements.models import (
    Achievement,
    AchievementTierChoices,
)
from life_dashboard.achievements.models import (
    UserAchievement as DjangoUserAchievement,
)
from life_dashboard.common.value_objects import UserId

pytestmark = pytest.mark.django_db


def _create_user(username: str = "test-user"):
    User = get_user_model()
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="secure-pass-123",
    )


def _create_achievement(name: str = "Test Achievement"):
    return Achievement.objects.create(
        name=name,
        description="Test achievement description",
        tier=AchievementTierChoices.BRONZE,
        icon="trophy",
        experience_reward=100,
        required_level=1,
        required_quest_completions=1,
    )


def test_user_achievement_repository_save_returns_existing_on_duplicate_unlock():
    """Concurrent duplicate unlock attempts should be idempotent."""

    user = _create_user()
    achievement = _create_achievement()
    repository = DjangoUserAchievementRepository()

    first_unlock = DomainUserAchievement(
        user_id=UserId(user.id),
        achievement_id=AchievementId(achievement.id),
        unlocked_at=datetime.now(timezone.utc),
        notes="First unlock",
    )

    saved_first = repository.save(first_unlock)

    duplicate_unlock = DomainUserAchievement(
        user_id=UserId(user.id),
        achievement_id=AchievementId(achievement.id),
        unlocked_at=datetime.now(timezone.utc),
        notes="Duplicate attempt",
    )

    saved_duplicate = repository.save(duplicate_unlock)

    assert saved_first.user_achievement_id is not None
    assert saved_duplicate.user_achievement_id == saved_first.user_achievement_id
    assert saved_duplicate.notes == saved_first.notes
    assert DjangoUserAchievement.objects.count() == 1
