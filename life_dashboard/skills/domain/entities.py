"""Domain entities for the skills context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from .value_objects import PracticeSession, SkillIdentifier, SkillProgress, UserIdentifier


@dataclass(frozen=True)
class SkillProfile:
    """Aggregate representing a user's relationship with a particular skill."""

    skill_id: SkillIdentifier
    user_id: UserIdentifier
    name: str
    category: str
    progress: SkillProgress

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Skill name cannot be empty")
        if not self.category:
            raise ValueError("Skill category cannot be empty")

    @property
    def current_level(self) -> int:
        return self.progress.current_level

    @property
    def experience_points(self) -> int:
        return self.progress.experience_points

    @property
    def last_practiced(self) -> Optional[datetime]:
        return self.progress.last_practiced

    def progress_percentage(self, additional_progress: int = 0) -> float:
        return self.progress.progress_percentage(additional_progress)

    def next_milestone(self) -> int:
        return self.progress.next_milestone()

    def days_since_practice(self, reference: datetime) -> Optional[int]:
        return self.progress.days_since_practice(reference)


@dataclass(frozen=True)
class SkillPortfolio:
    """Aggregate collection of skills belonging to a user."""

    user_id: UserIdentifier
    skills: tuple[SkillProfile, ...]

    def __post_init__(self) -> None:
        skill_user_ids = {skill.user_id for skill in self.skills}
        if skill_user_ids and skill_user_ids != {self.user_id}:
            raise ValueError("All skills must belong to the portfolio owner")

    def __iter__(self) -> Iterable[SkillProfile]:
        return iter(self.skills)

    def total_experience(self) -> int:
        return sum(skill.experience_points for skill in self.skills)

    def total_skills(self) -> int:
        return len(self.skills)


@dataclass(frozen=True)
class PracticeHistory:
    """Collection of practice sessions grouped per user."""

    user_id: UserIdentifier
    sessions: tuple[PracticeSession, ...]

    def __iter__(self) -> Iterable[PracticeSession]:
        return iter(self.sessions)

    def sessions_for_skill(self, skill_id: SkillIdentifier) -> tuple[PracticeSession, ...]:
        return tuple(session for session in self.sessions if session.skill_id == skill_id)
