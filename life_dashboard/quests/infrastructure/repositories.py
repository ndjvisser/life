"""
Quests infrastructure repositories - Django ORM implementations.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum

from ..domain.entities import Habit as DomainHabit
from ..domain.entities import HabitCompletion as DomainHabitCompletion
from ..domain.entities import HabitFrequency, QuestDifficulty, QuestStatus, QuestType
from ..domain.entities import Quest as DomainQuest
from ..domain.repositories import (
    HabitCompletionRepository,
    HabitRepository,
    QuestRepository,
)
from ..models import Habit as DjangoHabit
from ..models import HabitCompletion as DjangoHabitCompletion
from ..models import Quest as DjangoQuest


class DjangoQuestRepository(QuestRepository):
    """Django ORM implementation of QuestRepository."""

    def _to_domain(self, django_quest: DjangoQuest) -> DomainQuest:
        """Convert Django model to domain entity."""
        return DomainQuest(
            quest_id=str(django_quest.id),
            user_id=django_quest.user.id,
            title=django_quest.title,
            description=django_quest.description,
            quest_type=QuestType(django_quest.quest_type),
            difficulty=QuestDifficulty(django_quest.difficulty),
            status=QuestStatus(django_quest.status),
            experience_reward=django_quest.experience_reward,
            completion_percentage=0.0,  # Not in current model
            start_date=django_quest.start_date,
            due_date=django_quest.due_date,
            completed_at=django_quest.completed_at,
            parent_quest_id=str(django_quest.parent_quest.id)
            if django_quest.parent_quest
            else None,
            prerequisite_quest_ids=[],  # Not in current model
            created_at=django_quest.created_at,
            updated_at=django_quest.updated_at,
        )

    def _from_domain(
        self, domain_quest: DomainQuest, django_quest: Optional[DjangoQuest] = None
    ) -> DjangoQuest:
        """Convert domain entity to Django model."""
        if django_quest is None:
            user = User.objects.get(id=domain_quest.user_id)
            django_quest = DjangoQuest(user=user)

        django_quest.title = domain_quest.title
        django_quest.description = domain_quest.description
        django_quest.quest_type = domain_quest.quest_type.value
        django_quest.difficulty = domain_quest.difficulty.value
        django_quest.status = domain_quest.status.value
        django_quest.experience_reward = domain_quest.experience_reward
        django_quest.start_date = domain_quest.start_date
        django_quest.due_date = domain_quest.due_date
        django_quest.completed_at = domain_quest.completed_at

        if domain_quest.updated_at:
            django_quest.updated_at = domain_quest.updated_at

        return django_quest

    def get_by_id(self, quest_id: str) -> Optional[DomainQuest]:
        """Get quest by ID."""
        try:
            django_quest = DjangoQuest.objects.select_related("user").get(
                id=int(quest_id)
            )
            return self._to_domain(django_quest)
        except (DjangoQuest.DoesNotExist, ValueError):
            return None

    def get_by_user_id(self, user_id: int) -> List[DomainQuest]:
        """Get all quests for a user."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_status(self, user_id: int, status: QuestStatus) -> List[DomainQuest]:
        """Get quests by status for a user."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id, status=status.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_type(self, user_id: int, quest_type: QuestType) -> List[DomainQuest]:
        """Get quests by type for a user."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id, quest_type=quest_type.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def save(self, quest: DomainQuest) -> DomainQuest:
        """Save quest and return updated entity."""
        try:
            django_quest = DjangoQuest.objects.select_related("user").get(
                id=int(quest.quest_id)
            )
            django_quest = self._from_domain(quest, django_quest)
            django_quest.save()
            return self._to_domain(django_quest)
        except (DjangoQuest.DoesNotExist, ValueError) as err:
            raise ValueError(f"Quest {quest.quest_id} not found") from err

    def create(self, quest: DomainQuest) -> DomainQuest:
        """Create new quest."""
        django_quest = self._from_domain(quest)
        django_quest.save()
        # Update quest_id with the generated ID
        quest.quest_id = str(django_quest.id)
        return self._to_domain(django_quest)

    def delete(self, quest_id: str) -> bool:
        """Delete quest."""
        try:
            DjangoQuest.objects.get(id=int(quest_id)).delete()
            return True
        except (DjangoQuest.DoesNotExist, ValueError):
            return False

    def get_overdue_quests(self, user_id: int) -> List[DomainQuest]:
        """Get overdue quests for a user."""
        today = date.today()
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(
                user_id=user_id, due_date__lt=today, status__in=["active", "paused"]
            )
            .order_by("due_date")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_due_soon(self, user_id: int, days: int = 7) -> List[DomainQuest]:
        """Get quests due within specified days."""
        today = date.today()
        future_date = today + timedelta(days=days)
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(
                user_id=user_id,
                due_date__gte=today,
                due_date__lte=future_date,
                status="active",
            )
            .order_by("due_date")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_parent_quest(self, parent_quest_id: str) -> List[DomainQuest]:
        """Get child quests of a parent quest."""
        try:
            django_quests = (
                DjangoQuest.objects.select_related("user")
                .filter(parent_quest_id=int(parent_quest_id))
                .order_by("created_at")
            )
            return [self._to_domain(q) for q in django_quests]
        except ValueError:
            return []

    def search_quests(
        self, user_id: int, query: str, limit: int = 20
    ) -> List[DomainQuest]:
        """Search quests by title or description."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id)
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .order_by("-created_at")[:limit]
        )
        return [self._to_domain(q) for q in django_quests]


class DjangoHabitRepository(HabitRepository):
    """Django ORM implementation of HabitRepository."""

    def _to_domain(self, django_habit: DjangoHabit) -> DomainHabit:
        """Convert Django model to domain entity."""
        return DomainHabit(
            habit_id=str(django_habit.id),
            user_id=django_habit.user.id,
            name=django_habit.name,
            description=django_habit.description,
            frequency=HabitFrequency(django_habit.frequency),
            target_count=django_habit.target_count,
            current_streak=django_habit.current_streak,
            longest_streak=django_habit.longest_streak,
            experience_reward=django_habit.experience_reward,
            created_at=django_habit.created_at,
            updated_at=django_habit.updated_at,
            last_completed=django_habit.last_practiced,  # Map to last_practiced
        )

    def _from_domain(
        self, domain_habit: DomainHabit, django_habit: Optional[DjangoHabit] = None
    ) -> DjangoHabit:
        """Convert domain entity to Django model."""
        if django_habit is None:
            user = User.objects.get(id=domain_habit.user_id)
            django_habit = DjangoHabit(user=user)

        django_habit.name = domain_habit.name
        django_habit.description = domain_habit.description
        django_habit.frequency = domain_habit.frequency.value
        django_habit.target_count = domain_habit.target_count
        django_habit.current_streak = domain_habit.current_streak
        django_habit.longest_streak = domain_habit.longest_streak
        django_habit.experience_reward = domain_habit.experience_reward
        django_habit.last_practiced = domain_habit.last_completed

        if domain_habit.updated_at:
            django_habit.updated_at = domain_habit.updated_at

        return django_habit

    def get_by_id(self, habit_id: str) -> Optional[DomainHabit]:
        """Get habit by ID."""
        try:
            django_habit = DjangoHabit.objects.select_related("user").get(
                id=int(habit_id)
            )
            return self._to_domain(django_habit)
        except (DjangoHabit.DoesNotExist, ValueError):
            return None

    def get_by_user_id(self, user_id: int) -> List[DomainHabit]:
        """Get all habits for a user."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-created_at")
        )
        return [self._to_domain(h) for h in django_habits]

    def get_by_frequency(
        self, user_id: int, frequency: HabitFrequency
    ) -> List[DomainHabit]:
        """Get habits by frequency for a user."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id, frequency=frequency.value)
            .order_by("-created_at")
        )
        return [self._to_domain(h) for h in django_habits]

    def save(self, habit: DomainHabit) -> DomainHabit:
        """Save habit and return updated entity."""
        try:
            django_habit = DjangoHabit.objects.select_related("user").get(
                id=int(habit.habit_id)
            )
            django_habit = self._from_domain(habit, django_habit)
            django_habit.save()
            return self._to_domain(django_habit)
        except (DjangoHabit.DoesNotExist, ValueError) as err:
            raise ValueError(f"Habit {habit.habit_id} not found") from err

    def create(self, habit: DomainHabit) -> DomainHabit:
        """Create new habit."""
        django_habit = self._from_domain(habit)
        django_habit.save()
        # Update habit_id with the generated ID
        habit.habit_id = str(django_habit.id)
        return self._to_domain(django_habit)

    def delete(self, habit_id: str) -> bool:
        """Delete habit."""
        try:
            DjangoHabit.objects.get(id=int(habit_id)).delete()
            return True
        except (DjangoHabit.DoesNotExist, ValueError):
            return False

    def get_due_today(self, user_id: int) -> List[DomainHabit]:
        """Get habits due today for a user."""
        # This is a simplified implementation
        # In reality, we'd need to check completion history
        today = date.today()
        yesterday = today - timedelta(days=1)

        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id)
            .filter(
                Q(last_practiced__isnull=True)  # Never completed
                | Q(
                    last_practiced__lt=yesterday, frequency="daily"
                )  # Daily habits not done yesterday
                | Q(
                    last_practiced__lt=today - timedelta(days=7), frequency="weekly"
                )  # Weekly habits
                | Q(
                    last_practiced__lt=today - timedelta(days=30), frequency="monthly"
                )  # Monthly habits
            )
        )
        return [self._to_domain(h) for h in django_habits]

    def get_active_streaks(
        self, user_id: int, min_streak: int = 7
    ) -> List[DomainHabit]:
        """Get habits with active streaks above minimum."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id, current_streak__gte=min_streak)
            .order_by("-current_streak")
        )
        return [self._to_domain(h) for h in django_habits]

    def search_habits(
        self, user_id: int, query: str, limit: int = 20
    ) -> List[DomainHabit]:
        """Search habits by name or description."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id)
            .filter(Q(name__icontains=query) | Q(description__icontains=query))
            .order_by("-created_at")[:limit]
        )
        return [self._to_domain(h) for h in django_habits]


class DjangoHabitCompletionRepository(HabitCompletionRepository):
    """Django ORM implementation of HabitCompletionRepository."""

    def _to_domain(
        self, django_completion: DjangoHabitCompletion
    ) -> DomainHabitCompletion:
        """Convert Django model to domain entity."""
        return DomainHabitCompletion(
            completion_id=str(django_completion.id),
            habit_id=str(django_completion.habit.id),
            user_id=django_completion.habit.user.id,
            completion_date=django_completion.date,
            count=django_completion.count,
            notes=django_completion.notes,
            experience_gained=django_completion.experience_gained,
            streak_at_completion=0,  # Not in current model
            created_at=django_completion.date,  # Use date as created_at
        )

    def _from_domain(
        self, domain_completion: DomainHabitCompletion
    ) -> DjangoHabitCompletion:
        """Convert domain entity to Django model."""
        habit = DjangoHabit.objects.get(id=int(domain_completion.habit_id))

        return DjangoHabitCompletion(
            habit=habit,
            date=domain_completion.completion_date,
            count=domain_completion.count,
            notes=domain_completion.notes,
            experience_gained=domain_completion.experience_gained,
        )

    def create(self, completion: DomainHabitCompletion) -> DomainHabitCompletion:
        """Create new habit completion."""
        django_completion = self._from_domain(completion)
        django_completion.save()
        # Update completion_id with the generated ID
        completion.completion_id = str(django_completion.id)
        return self._to_domain(django_completion)

    def get_by_habit_id(
        self, habit_id: str, limit: int = 100
    ) -> List[DomainHabitCompletion]:
        """Get completions for a habit."""
        try:
            django_completions = (
                DjangoHabitCompletion.objects.select_related("habit__user")
                .filter(habit_id=int(habit_id))
                .order_by("-date")[:limit]
            )
            return [self._to_domain(c) for c in django_completions]
        except ValueError:
            return []

    def get_by_user_id(
        self, user_id: int, limit: int = 100
    ) -> List[DomainHabitCompletion]:
        """Get completions for a user."""
        django_completions = (
            DjangoHabitCompletion.objects.select_related("habit__user")
            .filter(habit__user_id=user_id)
            .order_by("-date")[:limit]
        )
        return [self._to_domain(c) for c in django_completions]

    def get_by_date_range(
        self, habit_id: str, start_date: date, end_date: date
    ) -> List[DomainHabitCompletion]:
        """Get completions within date range."""
        try:
            django_completions = (
                DjangoHabitCompletion.objects.select_related("habit__user")
                .filter(
                    habit_id=int(habit_id), date__gte=start_date, date__lte=end_date
                )
                .order_by("date")
            )
            return [self._to_domain(c) for c in django_completions]
        except ValueError:
            return []

    def get_completion_for_date(
        self, habit_id: str, completion_date: date
    ) -> Optional[DomainHabitCompletion]:
        """Get completion for specific date."""
        try:
            django_completion = DjangoHabitCompletion.objects.select_related(
                "habit__user"
            ).get(habit_id=int(habit_id), date=completion_date)
            return self._to_domain(django_completion)
        except (DjangoHabitCompletion.DoesNotExist, ValueError):
            return None

    def delete_completion(self, completion_id: str) -> bool:
        """Delete habit completion."""
        try:
            DjangoHabitCompletion.objects.get(id=int(completion_id)).delete()
            return True
        except (DjangoHabitCompletion.DoesNotExist, ValueError):
            return False

    def get_streak_data(
        self, habit_id: str, days: int = 365
    ) -> List[DomainHabitCompletion]:
        """Get completion data for streak calculation."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.get_by_date_range(habit_id, start_date, end_date)

    def get_completion_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get completion statistics for user."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        completions = DjangoHabitCompletion.objects.filter(
            habit__user_id=user_id, date__gte=start_date, date__lte=end_date
        )

        stats = completions.aggregate(
            total_completions=Count("id"),
            total_experience=Sum("experience_gained"),
        )

        # Calculate completion rate (simplified)
        total_habits = DjangoHabit.objects.filter(user_id=user_id).count()
        if total_habits > 0:
            stats["completion_rate"] = (
                (stats["total_completions"] or 0) / (total_habits * days) * 100
            )
        else:
            stats["completion_rate"] = 0.0

        return stats
