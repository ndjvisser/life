"""Domain services for producing skill analytics summaries."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from .entities import PracticeHistory, SkillPortfolio
from .repositories import PracticeRepository, SkillRepository
from .value_objects import UserIdentifier


@dataclass(frozen=True)
class RecommendedAction:
    """Actionable recommendation for the user."""

    description: str
    priority: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "description": self.description,
            "priority": self.priority,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SkillProgressSnapshot:
    """Snapshot of a skill's current progress."""

    skill_name: str
    current_level: int
    next_milestone: int
    progress_percentage: float
    recent_experience: int = 0

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "skill_name": self.skill_name,
            "current_level": self.current_level,
            "next_milestone": self.next_milestone,
            "progress_percentage": self.progress_percentage,
        }


@dataclass(frozen=True)
class StagnantSkill:
    """Represents a skill that has not been practiced recently."""

    name: str
    level: int
    days_since_practice: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "name": self.name,
            "level": self.level,
            "days_since_practice": self.days_since_practice,
        }


@dataclass(frozen=True)
class TopSkill:
    """Represents a high performing skill."""

    name: str
    level: int
    mastery: str
    rank: str

    def as_dict(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "level": self.level,
            "mastery": self.mastery,
            "rank": self.rank,
        }


@dataclass(frozen=True)
class SkillProgressSummary:
    """Domain DTO representing an aggregated view of the user's skills."""

    top_skills: list[TopSkill]
    stagnant_skills: list[StagnantSkill]
    active_skills: list[SkillProgressSnapshot]
    total_experience: int
    total_skills: int

    def as_dict(self) -> dict[str, object]:
        return {
            "top_skills": [skill.as_dict() for skill in self.top_skills],
            "stagnant_skills": [skill.as_dict() for skill in self.stagnant_skills],
            "active_skills": [skill.as_dict() for skill in self.active_skills],
            "total_experience": self.total_experience,
            "total_skills": self.total_skills,
        }


@dataclass(frozen=True)
class SkillProgressSummaryResponse:
    """Full API response representation."""

    user_id: int
    summary_generated_at: datetime
    skill_progress_summary: SkillProgressSummary
    recommended_actions: list[RecommendedAction]

    def as_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "summary_generated_at": self.summary_generated_at.isoformat(),
            "skill_progress_summary": self.skill_progress_summary.as_dict(),
            "recommended_actions": [
                action.as_dict() for action in self.recommended_actions
            ],
        }


class SkillProgressSummaryService:
    """Build skill progress summaries using repositories."""

    def __init__(
        self,
        skill_repository: SkillRepository,
        practice_repository: PracticeRepository,
        recency_window: timedelta | None = None,
        stagnation_threshold: timedelta | None = None,
    ) -> None:
        self._skills = skill_repository
        self._practice = practice_repository
        self._recency_window = recency_window or timedelta(days=30)
        self._stagnation_threshold = stagnation_threshold or timedelta(days=30)

    def _recent_experience_by_skill(
        self,
        history: PracticeHistory,
        as_of: datetime,
    ) -> dict[str, int]:
        """Group practice experience by skill within the recent window."""

        lower_bound = as_of - self._recency_window
        grouped: dict[str, int] = defaultdict(int)
        for session in history:
            if session.practiced_at > as_of:
                continue
            if session.practiced_at < lower_bound:
                continue
            grouped[session.skill_id.value] += session.experience_gained
        return grouped

    def _latest_practice_by_skill(
        self, history: PracticeHistory
    ) -> dict[str, datetime]:
        latest: dict[str, datetime] = {}
        for session in history:
            key = session.skill_id.value
            current = latest.get(key)
            if current is None or session.practiced_at > current:
                latest[key] = session.practiced_at
        return latest

    def _stagnant_skills(
        self,
        portfolio: SkillPortfolio,
        as_of: datetime,
        last_practiced_map: dict[str, datetime],
    ) -> list[StagnantSkill]:
        stagnant: list[StagnantSkill] = []
        for skill in portfolio:
            last_practiced = last_practiced_map.get(skill.skill_id.value)
            if last_practiced is not None:
                inactivity = as_of - last_practiced
                if inactivity < self._stagnation_threshold:
                    continue
                days = max(0, inactivity.days)
            else:
                days = skill.days_since_practice(as_of)
                threshold_days = self._stagnation_threshold.days
                if days is None or days < threshold_days:
                    continue
            stagnant.append(
                StagnantSkill(
                    name=skill.name,
                    level=skill.current_level,
                    days_since_practice=days,
                )
            )
        stagnant.sort(key=lambda entry: entry.days_since_practice, reverse=True)
        return stagnant

    @staticmethod
    def _determine_mastery(level: int) -> tuple[str, str]:
        if level >= 80:
            return "master", "Master"
        if level >= 60:
            return "expert", "Expert"
        if level >= 40:
            return "veteran", "Seasoned Adventurer"
        if level >= 30:
            return "apprentice", "Advanced Apprentice"
        if level >= 20:
            return "apprentice", "Skilled Apprentice"
        return "novice", "Developing"

    def _top_skills(self, portfolio: SkillPortfolio) -> list[TopSkill]:
        sorted_skills = sorted(
            portfolio,
            key=lambda skill: (skill.current_level, skill.experience_points),
            reverse=True,
        )
        top_entries: list[TopSkill] = []
        for skill in sorted_skills[:5]:
            mastery, rank = self._determine_mastery(skill.current_level)
            if mastery == "apprentice" and skill.current_level < 30:
                rank = "Skilled Apprentice"
            top_entries.append(
                TopSkill(
                    name=skill.name,
                    level=skill.current_level,
                    mastery=mastery,
                    rank=rank,
                )
            )
        return top_entries

    def _active_skills(
        self,
        portfolio: SkillPortfolio,
        recent_xp: dict[str, int],
    ) -> list[SkillProgressSnapshot]:
        snapshots: list[SkillProgressSnapshot] = []
        for skill in portfolio:
            xp_gain = recent_xp.get(skill.skill_id.value, 0)
            progress = skill.progress_percentage()
            snapshots.append(
                SkillProgressSnapshot(
                    skill_name=skill.name,
                    current_level=skill.current_level,
                    next_milestone=skill.next_milestone(),
                    progress_percentage=progress,
                    recent_experience=xp_gain,
                )
            )
        snapshots.sort(
            key=lambda item: (item.recent_experience, item.progress_percentage),
            reverse=True,
        )
        return snapshots[:5]

    def _total_experience(
        self, portfolio: SkillPortfolio, recent_xp: dict[str, int]
    ) -> int:
        total = 0
        for skill in portfolio:
            xp_gain = recent_xp.get(skill.skill_id.value, 0)
            total += max(0, skill.experience_points - xp_gain)
        return total

    def _recommended_actions(
        self,
        stagnant: list[StagnantSkill],
        active: list[SkillProgressSnapshot],
    ) -> list[RecommendedAction]:
        actions: list[RecommendedAction] = []
        if stagnant:
            first = stagnant[0]
            urgency = "high" if first.days_since_practice >= 45 else "medium"
            actions.append(
                RecommendedAction(
                    description=f"Schedule practice session for {first.name}",
                    priority=urgency,
                    reason=f"No activity for {first.days_since_practice} days",
                )
            )
        if len(active) >= 1:
            focus_skill = active[0]
            actions.append(
                RecommendedAction(
                    description=(
                        f"Push {focus_skill.skill_name} to level "
                        f"{focus_skill.next_milestone}"
                    ),
                    priority="medium",
                    reason="Strong momentum towards next milestone",
                )
            )
        if len(active) >= 2:
            maint = active[-1]
            actions.append(
                RecommendedAction(
                    description=f"Maintain fundamentals in {maint.skill_name}",
                    priority="low",
                    reason="Consistent small gains keep mastery sharp",
                )
            )
        return actions

    def generate_summary(
        self,
        user_id: int,
        as_of: datetime | None = None,
    ) -> SkillProgressSummaryResponse:
        as_of = as_of or datetime.utcnow()
        user_identifier = UserIdentifier(user_id)
        portfolio = self._skills.portfolio_for_user(user_identifier)
        history = self._practice.history_for_user(user_identifier)

        recent_xp = self._recent_experience_by_skill(history, as_of)
        active_skills = self._active_skills(portfolio, recent_xp)
        last_practiced = self._latest_practice_by_skill(history)
        stagnant = self._stagnant_skills(portfolio, as_of, last_practiced)
        top_skills = self._top_skills(portfolio)

        summary = SkillProgressSummary(
            top_skills=top_skills,
            stagnant_skills=stagnant,
            active_skills=active_skills,
            total_experience=self._total_experience(portfolio, recent_xp),
            total_skills=portfolio.total_skills(),
        )
        actions = self._recommended_actions(stagnant, active_skills)
        return SkillProgressSummaryResponse(
            user_id=user_id,
            summary_generated_at=as_of,
            skill_progress_summary=summary,
            recommended_actions=actions,
        )


def build_skill_progress_summary_response(
    service: SkillProgressSummaryService,
    user_id: int,
    as_of: datetime | None = None,
) -> dict[str, object]:
    """Utility helper returning a serialisable summary for tests/API."""

    response = service.generate_summary(user_id=user_id, as_of=as_of)
    return response.as_dict()
