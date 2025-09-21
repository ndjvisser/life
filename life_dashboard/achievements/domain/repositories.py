"""Repository interfaces for achievements domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import AchievementTracker
from .value_objects import UserIdentifier


class AchievementRepository(ABC):
    """Repository providing access to achievements progress."""

    @abstractmethod
    def tracker_for_user(self, user_id: UserIdentifier) -> AchievementTracker:
        """Return the achievement tracker for the supplied user."""
