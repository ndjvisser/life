"""
Quests application services - use case orchestration and business workflows.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from ..domain.entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestStatus,
    QuestType,
)
from ..domain.repositories import (
    HabitCompletionRepository,
    HabitRepository,
    QuestRepository,
)


class QuestService:
    """Service for quest management and workflows."""

    def __init__(self, quest_repo: QuestRepository):
        self.quest_repo = quest_repo

    def create_quest(
        self,
        user_id: int,
        title: str,
        description: str = "",
        quest_type: QuestType = QuestType.MAIN,
        difficulty: str = "medium",
        experience_reward: int = 10,
        due_date: Optional[date] = None,
    ) -> Quest:
        """Create a new quest."""
        quest = Quest(
            user_id=user_id,
            title=title,
            description=description,
            quest_type=quest_type,
            difficulty=getattr(
                Quest.QuestDifficulty, difficulty.upper(), Quest.QuestDifficulty.MEDIUM
            ),
            experience_reward=experience_reward,
            due_date=due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return self.quest_repo.create(quest)

    def start_quest(self, quest_id: str) -> Quest:
        """Start a quest."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.start_quest()
        return self.quest_repo.save(quest)

    def complete_quest(self, quest_id: str) -> Tuple[Quest, int]:
        """
        Complete a quest.

        Returns:
            tuple: (updated_quest, experience_awarded)
        """
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        experience_reward, completion_time = quest.complete_quest()
        updated_quest = self.quest_repo.save(quest)

        # Calculate final experience with difficulty bonus
        final_experience = quest.calculate_final_experience()

        return updated_quest, final_experience

    def update_quest_progress(self, quest_id: str, percentage: float) -> Quest:
        """Update quest progress percentage."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.update_progress(percentage)
        return self.quest_repo.save(quest)

    def pause_quest(self, quest_id: str) -> Quest:
        """Pause an active quest."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.pause_quest()
        return self.quest_repo.save(quest)

    def resume_quest(self, quest_id: str) -> Quest:
        """Resume a paused quest."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.resume_quest()
        return self.quest_repo.save(quest)

    def fail_quest(self, quest_id: str, reason: str = "") -> Quest:
        """Mark quest as failed."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.fail_quest(reason)
        return self.quest_repo.save(quest)

    def get_user_quests(
        self,
        user_id: int,
        status: Optional[QuestStatus] = None,
        quest_type: Optional[QuestType] = None,
    ) -> List[Quest]:
        """Get quests for a user with optional filtering."""
        if status:
            return self.quest_repo.get_by_status(user_id, status)
        elif quest_type:
            return self.quest_repo.get_by_type(user_id, quest_type)
        else:
            return self.quest_repo.get_by_user_id(user_id)

    def get_overdue_quests(self, user_id: int) -> List[Quest]:
        """Get overdue quests for a user."""
        return self.quest_repo.get_overdue_quests(user_id)

    def get_upcoming_quests(self, user_id: int, days: int = 7) -> List[Quest]:
        """Get quests due within specified days."""
        return self.quest_repo.get_due_soon(user_id, days)

    def delete_quest(self, quest_id: str) -> bool:
        """Delete a quest."""
        return self.quest_repo.delete(quest_id)

    def search_quests(self, user_id: int, query: str, limit: int = 20) -> List[Quest]:
        """Search user's quests."""
        return self.quest_repo.search_quests(user_id, query, limit)

    def get_quest_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get quest statistics for a user."""
        all_quests = self.quest_repo.get_by_user_id(user_id)

        stats = {
            "total_quests": len(all_quests),
            "active_quests": len(
                [q for q in all_quests if q.status == QuestStatus.ACTIVE]
            ),
            "completed_quests": len(
                [q for q in all_quests if q.status == QuestStatus.COMPLETED]
            ),
            "failed_quests": len(
                [q for q in all_quests if q.status == QuestStatus.FAILED]
            ),
            "overdue_quests": len([q for q in all_quests if q.is_overdue()]),
            "completion_rate": 0.0,
            "total_experience_earned": 0,
            "average_completion_time": 0.0,
        }

        completed_quests = [q for q in all_quests if q.status == QuestStatus.COMPLETED]
        if completed_quests:
            stats["completion_rate"] = (len(completed_quests) / len(all_quests)) * 100
            stats["total_experience_earned"] = sum(
                q.calculate_final_experience() for q in completed_quests
            )

        return stats


class HabitService:
    """Service for habit management and tracking."""

    def __init__(
        self, habit_repo: HabitRepository, completion_repo: HabitCompletionRepository
    ):
        self.habit_repo = habit_repo
        self.completion_repo = completion_repo

    def create_habit(
        self,
        user_id: int,
        name: str,
        description: str = "",
        frequency: HabitFrequency = HabitFrequency.DAILY,
        target_count: int = 1,
        experience_reward: int = 5,
    ) -> Habit:
        """Create a new habit."""
        habit = Habit(
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency,
            target_count=target_count,
            experience_reward=experience_reward,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return self.habit_repo.create(habit)

    def complete_habit(
        self,
        habit_id: str,
        completion_date: Optional[date] = None,
        count: int = 1,
        notes: str = "",
    ) -> Tuple[Habit, HabitCompletion, int]:
        """
        Complete a habit.

        Returns:
            tuple: (updated_habit, completion_record, experience_gained)
        """
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id} not found")

        if not completion_date:
            completion_date = date.today()

        # Check if already completed today
        existing_completion = self.completion_repo.get_completion_for_date(
            habit_id, completion_date
        )
        if existing_completion:
            raise ValueError(f"Habit already completed on {completion_date}")

        # Complete the habit (updates streak)
        experience_gained, new_streak, milestone_reached = habit.complete_habit(
            completion_date
        )

        # Save updated habit
        updated_habit = self.habit_repo.save(habit)

        # Create completion record
        completion = HabitCompletion(
            habit_id=habit_id,
            user_id=habit.user_id,
            completion_date=completion_date,
            count=count,
            notes=notes,
            experience_gained=experience_gained,
            streak_at_completion=new_streak,
            created_at=datetime.utcnow(),
        )

        saved_completion = self.completion_repo.create(completion)

        return updated_habit, saved_completion, experience_gained

    def break_habit_streak(self, habit_id: str) -> Habit:
        """Break a habit's current streak."""
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id} not found")

        habit.break_streak()
        return self.habit_repo.save(habit)

    def get_user_habits(
        self, user_id: int, frequency: Optional[HabitFrequency] = None
    ) -> List[Habit]:
        """Get habits for a user with optional frequency filter."""
        if frequency:
            return self.habit_repo.get_by_frequency(user_id, frequency)
        else:
            return self.habit_repo.get_by_user_id(user_id)

    def get_habits_due_today(self, user_id: int) -> List[Habit]:
        """Get habits due today for a user."""
        return self.habit_repo.get_due_today(user_id)

    def get_active_streaks(self, user_id: int, min_streak: int = 7) -> List[Habit]:
        """Get habits with active streaks."""
        return self.habit_repo.get_active_streaks(user_id, min_streak)

    def get_habit_completions(
        self, habit_id: str, limit: int = 30
    ) -> List[HabitCompletion]:
        """Get recent completions for a habit."""
        return self.completion_repo.get_by_habit_id(habit_id, limit)

    def get_completion_history(
        self, habit_id: str, start_date: date, end_date: date
    ) -> List[HabitCompletion]:
        """Get completion history within date range."""
        return self.completion_repo.get_by_date_range(habit_id, start_date, end_date)

    def delete_habit(self, habit_id: str) -> bool:
        """Delete a habit."""
        return self.habit_repo.delete(habit_id)

    def delete_completion(self, completion_id: str) -> bool:
        """Delete a habit completion."""
        return self.completion_repo.delete_completion(completion_id)

    def search_habits(self, user_id: int, query: str, limit: int = 20) -> List[Habit]:
        """Search user's habits."""
        return self.habit_repo.search_habits(user_id, query, limit)

    def get_habit_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get habit statistics for a user."""
        habits = self.habit_repo.get_by_user_id(user_id)
        completion_stats = self.completion_repo.get_completion_stats(user_id, days)

        stats = {
            "total_habits": len(habits),
            "active_streaks": len([h for h in habits if h.current_streak > 0]),
            "longest_streak": max([h.longest_streak for h in habits], default=0),
            "total_completions": completion_stats.get("total_completions", 0),
            "completion_rate": completion_stats.get("completion_rate", 0.0),
            "total_experience_earned": completion_stats.get("total_experience", 0),
            "streak_milestones": len([h for h in habits if h.current_streak >= 7]),
            "habits_due_today": len(self.get_habits_due_today(user_id)),
        }

        return stats


class QuestChainService:
    """Service for managing quest chains and dependencies."""

    def __init__(self, quest_repo: QuestRepository):
        self.quest_repo = quest_repo

    def create_quest_chain(
        self, user_id: int, parent_quest_id: str, child_quests: List[Dict[str, Any]]
    ) -> List[Quest]:
        """Create a chain of dependent quests."""
        created_quests = []

        for quest_data in child_quests:
            quest = Quest(
                user_id=user_id,
                parent_quest_id=parent_quest_id,
                **quest_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            created_quest = self.quest_repo.create(quest)
            created_quests.append(created_quest)

        return created_quests

    def get_quest_chain(self, parent_quest_id: str) -> List[Quest]:
        """Get all child quests in a chain."""
        return self.quest_repo.get_by_parent_quest(parent_quest_id)

    def check_prerequisites(self, quest_id: str) -> bool:
        """Check if all prerequisite quests are completed."""
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest or not quest.prerequisite_quest_ids:
            return True

        for prereq_id in quest.prerequisite_quest_ids:
            prereq_quest = self.quest_repo.get_by_id(prereq_id)
            if not prereq_quest or prereq_quest.status != QuestStatus.COMPLETED:
                return False

        return True

    def unlock_next_quests(self, completed_quest_id: str) -> List[Quest]:
        """Unlock quests that had this quest as a prerequisite."""
        # Find quests that have this quest as a prerequisite
        all_quests = self.quest_repo.get_by_user_id(0)  # This would need user_id
        unlocked_quests = []

        for quest in all_quests:
            if (
                completed_quest_id in quest.prerequisite_quest_ids
                and quest.status == QuestStatus.DRAFT
                and self.check_prerequisites(quest.quest_id)
            ):
                quest.status = QuestStatus.ACTIVE
                updated_quest = self.quest_repo.save(quest)
                unlocked_quests.append(updated_quest)

        return unlocked_quests
