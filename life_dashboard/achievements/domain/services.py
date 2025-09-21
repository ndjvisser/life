"""Domain services for achievement progress reporting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .entities import AchievementTracker
from .repositories import AchievementRepository
from .value_objects import UserIdentifier


@dataclass(frozen=True)
class AchievementProgressSnapshot:
    name: str
    description: str
    tier: str
    completion_percentage: float
    reward_points: int
    remaining_progress: int

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "tier": self.tier,
            "completion_percentage": self.completion_percentage,
            "reward_points": self.reward_points,
            "remaining_progress": self.remaining_progress,
        }


@dataclass(frozen=True)
class AchievementProgressSummary:
    tracked: list[AchievementProgressSnapshot]
    completed: list[AchievementProgressSnapshot]
    highest_potential_reward: int
    total_tracked: int

    def as_dict(self) -> dict[str, object]:
        return {
            "tracked": [item.as_dict() for item in self.tracked],
            "completed": [item.as_dict() for item in self.completed],
            "highest_potential_reward": self.highest_potential_reward,
            "total_tracked": self.total_tracked,
        }


@dataclass(frozen=True)
class AchievementProgressResponse:
    user_id: int
    generated_at: datetime
    achievement_progress: AchievementProgressSummary

    def as_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "generated_at": self.generated_at.isoformat(),
            "achievement_progress": self.achievement_progress.as_dict(),
        }


class AchievementProgressService:
    """Service orchestrating achievement progress summary generation."""

    def __init__(self, achievement_repository: AchievementRepository) -> None:
        self._repository = achievement_repository

    def _build_snapshots(
        self,
        tracker: AchievementTracker,
    ) -> tuple[list[AchievementProgressSnapshot], list[AchievementProgressSnapshot]]:
        completed: list[AchievementProgressSnapshot] = []
        tracked: list[AchievementProgressSnapshot] = []
        for achievement in tracker.achievements:
            snapshot = AchievementProgressSnapshot(
                name=achievement.name,
                description=achievement.description,
                tier=achievement.tier,
                completion_percentage=round(achievement.completion_percentage, 2),
                reward_points=achievement.reward_points,
                remaining_progress=achievement.remaining_progress,
            )
            if achievement.completion_percentage >= 100:
                completed.append(snapshot)
            else:
                tracked.append(snapshot)
        return tracked, completed

    def generate(
        self,
        user_id: int,
        as_of: datetime | None = None,
    ) -> AchievementProgressResponse:
        tracker = self._repository.tracker_for_user(UserIdentifier(user_id))
        tracked, completed = self._build_snapshots(tracker)
        summary = AchievementProgressSummary(
            tracked=tracked,
            completed=completed,
            highest_potential_reward=tracker.highest_reward(),
            total_tracked=len(tracker.achievements),
        )
        return AchievementProgressResponse(
            user_id=user_id,
            generated_at=as_of or datetime.utcnow(),
            achievement_progress=summary,
        )


def build_achievement_progress_response(
    service: AchievementProgressService,
    user_id: int,
    as_of: datetime | None = None,
) -> dict[str, object]:
    response = service.generate(user_id=user_id, as_of=as_of)
    return response.as_dict()
