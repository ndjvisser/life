"""Domain entities for achievements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .value_objects import AchievementProgress, UserIdentifier


@dataclass(frozen=True)
class AchievementTracker:
    """Collection of achievements currently tracked for a user."""

    user_id: UserIdentifier
    achievements: tuple[AchievementProgress, ...]

    def __iter__(self) -> Iterable[AchievementProgress]:
        return iter(self.achievements)

    def completed(self) -> list[AchievementProgress]:
        return [a for a in self.achievements if a.completion_percentage >= 100]

    def in_progress(self) -> list[AchievementProgress]:
        return [a for a in self.achievements if a.completion_percentage < 100]

    def highest_reward(self) -> int:
        rewards = [achievement.reward_points for achievement in self.achievements]
        rewards.extend(
            achievement.potential_reward
            for achievement in self.achievements
            if achievement.potential_reward is not None
        )
        return max(rewards) if rewards else 0
