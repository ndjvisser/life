"""
Quest Domain Services

Pure business logic services for quest and habit operations.
No Django dependencies allowed in this module.
"""

from datetime import date, datetime, timedelta

from .entities import Habit, HabitCompletion, Quest, QuestStatus, QuestType
from .repositories import HabitCompletionRepository, HabitRepository, QuestRepository
from .value_objects import CompletionCount, ExperienceReward, HabitId, QuestId, UserId


class QuestService:
    """Service for quest business operations"""

    def __init__(self, quest_repository: QuestRepository):
        self._quest_repository = quest_repository

    def create_quest(
        self,
        user_id: UserId,
        title: str,
        description: str,
        difficulty: str,
        quest_type: str,
        experience_reward: int,
        start_date: date | None = None,
        due_date: date | None = None,
    ) -> Quest:
        """Create a new quest with validation"""
        from .entities import QuestDifficulty
        from .value_objects import ExperienceReward, QuestDescription, QuestTitle

        # Convert string enums to domain enums
        difficulty_enum = QuestDifficulty(difficulty)
        type_enum = QuestType(quest_type)

        # Create value objects with validation
        quest_title = QuestTitle(title)
        quest_description = QuestDescription(description)
        exp_reward = ExperienceReward(experience_reward)

        # Generate quest ID (in real implementation, this would come from repository)
        quest_id = QuestId(1)  # Placeholder

        quest = Quest(
            quest_id=quest_id,
            user_id=user_id,
            title=quest_title,
            description=quest_description,
            difficulty=difficulty_enum,
            quest_type=type_enum,
            status=QuestStatus.DRAFT,
            experience_reward=exp_reward,
            start_date=start_date,
            due_date=due_date,
        )

        return self._quest_repository.save(quest)

    def activate_quest(self, quest_id: QuestId) -> Quest:
        """Activate a quest"""
        quest = self._quest_repository.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id.value} not found")

        quest.activate()
        return self._quest_repository.save(quest)

    def complete_quest(self, quest_id: QuestId) -> tuple[Quest, int]:
        """Complete a quest and return experience gained"""
        quest = self._quest_repository.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id.value} not found")

        quest.complete()
        experience_gained = quest.calculate_final_experience()

        updated_quest = self._quest_repository.save(quest)
        return updated_quest, experience_gained

    def fail_quest(self, quest_id: QuestId) -> Quest:
        """Mark a quest as failed"""
        quest = self._quest_repository.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id.value} not found")

        quest.fail()
        return self._quest_repository.save(quest)

    def get_overdue_quests(self, user_id: UserId) -> list[Quest]:
        """Get all overdue quests for a user"""
        active_quests = self._quest_repository.get_active_quests(user_id)
        return [quest for quest in active_quests if quest.is_overdue()]

    def calculate_quest_completion_rate(self, user_id: UserId, days: int = 30) -> float:
        """Calculate quest completion rate for a user over specified days"""
        all_quests = self._quest_repository.get_by_user_id(user_id)

        # Filter quests from the last N days
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        recent_quests = [
            quest for quest in all_quests if quest.created_at.date() >= cutoff_date
        ]

        if not recent_quests:
            return 0.0

        completed_quests = [
            quest for quest in recent_quests if quest.status == QuestStatus.COMPLETED
        ]

        return len(completed_quests) / len(recent_quests)


class HabitService:
    """Service for habit business operations"""

    def __init__(
        self,
        habit_repository: HabitRepository,
        completion_repository: HabitCompletionRepository,
    ):
        self._habit_repository = habit_repository
        self._completion_repository = completion_repository

    def create_habit(
        self,
        user_id: UserId,
        name: str,
        description: str,
        frequency: str,
        target_count: int,
        experience_reward: int,
    ) -> Habit:
        """Create a new habit with validation"""
        from .entities import HabitFrequency
        from .value_objects import (
            CompletionCount,
            ExperienceReward,
            HabitName,
            StreakCount,
        )

        # Convert and validate inputs
        frequency_enum = HabitFrequency(frequency)
        habit_name = HabitName(name)
        target = CompletionCount(target_count)
        exp_reward = ExperienceReward(experience_reward)

        # Generate habit ID (in real implementation, this would come from repository)
        habit_id = HabitId(1)  # Placeholder

        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=habit_name,
            description=description,
            frequency=frequency_enum,
            target_count=target,
            current_streak=StreakCount(0),
            longest_streak=StreakCount(0),
            experience_reward=exp_reward,
        )

        return self._habit_repository.save(habit)

    def complete_habit(
        self,
        habit_id: HabitId,
        completion_count: int = 1,
        completion_date: date | None = None,
        notes: str = "",
    ) -> tuple[HabitCompletion, int]:
        """Complete a habit and return completion record with experience gained"""
        habit = self._habit_repository.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id.value} not found")

        if completion_date is None:
            completion_date = date.today()

        # Get previous completion to calculate streak
        previous_completion = self._completion_repository.get_latest_completion(
            habit_id
        )
        previous_date = (
            previous_completion.completion_date if previous_completion else None
        )

        # Update habit streak
        habit.update_streak(completion_date, previous_date)

        # Calculate experience with streak bonus
        experience_gained = habit.calculate_experience_reward(completion_count)

        # Create completion record
        completion = HabitCompletion(
            completion_id="",  # Will be generated in __post_init__
            habit_id=habit_id,
            count=CompletionCount(completion_count),
            completion_date=completion_date,
            notes=notes,
            experience_gained=ExperienceReward(experience_gained),
        )

        # Save both habit and completion
        self._habit_repository.save(habit)
        saved_completion = self._completion_repository.save(completion)

        return saved_completion, experience_gained

    def calculate_habit_consistency(self, habit_id: HabitId, days: int = 30) -> float:
        """Calculate habit consistency over specified days"""
        habit = self._habit_repository.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id.value} not found")

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        completions = self._completion_repository.get_by_date_range(
            habit_id, start_date, end_date
        )

        # Calculate expected completions based on frequency
        expected_completions = self._calculate_expected_completions(habit, days)

        if expected_completions == 0:
            return 0.0

        actual_completions = len(completions)
        return min(actual_completions / expected_completions, 1.0)

    def _calculate_expected_completions(self, habit: Habit, days: int) -> int:
        """Calculate expected number of completions based on habit frequency"""
        from .entities import HabitFrequency

        if habit.frequency == HabitFrequency.DAILY:
            return days
        elif habit.frequency == HabitFrequency.WEEKLY:
            return days // 7
        elif habit.frequency == HabitFrequency.MONTHLY:
            return days // 30
        else:
            return days  # Custom frequency - assume daily

    def get_streak_milestones(self, habit_id: HabitId) -> list[str]:
        """Get achieved streak milestones for a habit"""
        habit = self._habit_repository.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id.value} not found")

        milestones = []
        streak = habit.current_streak.value

        milestone_thresholds = [7, 21, 30, 50, 100, 365]
        for threshold in milestone_thresholds:
            if streak >= threshold:
                milestones.append(f"{threshold}_day_streak")

        return milestones

    def break_habit_streak(self, habit_id: HabitId) -> Habit:
        """Break a habit streak (for missed days)"""
        habit = self._habit_repository.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit {habit_id.value} not found")

        habit.break_streak()
        return self._habit_repository.save(habit)
