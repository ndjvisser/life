"""
Fast unit tests for Quest domain entities.

These tests run without Django and focus on pure business logic validation.
"""

from datetime import date, datetime, timedelta

import pytest

from life_dashboard.quests.domain.entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestDifficulty,
    QuestStatus,
    QuestType,
)
from life_dashboard.quests.domain.value_objects import (
    CompletionCount,
    ExperienceReward,
    HabitId,
    HabitName,
    QuestDescription,
    QuestId,
    QuestTitle,
    StreakCount,
    UserId,
)


class TestQuest:
    """Test Quest domain entity"""

    def test_quest_creation_with_valid_data(self):
        """Test creating a quest with valid data"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Learn Python"),
            description=QuestDescription("Complete Python tutorial"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.DRAFT,
            experience_reward=ExperienceReward(100),
        )

        assert quest.quest_id.value == 1
        assert quest.title.value == "Learn Python"
        assert quest.status == QuestStatus.DRAFT
        assert quest.difficulty == QuestDifficulty.MEDIUM

    def test_quest_date_validation(self):
        """Test quest date validation"""
        with pytest.raises(ValueError, match="Start date cannot be after due date"):
            Quest(
                quest_id=QuestId(1),
                user_id=UserId(1),
                title=QuestTitle("Test Quest"),
                description=QuestDescription("Test"),
                difficulty=QuestDifficulty.EASY,
                quest_type=QuestType.DAILY,
                status=QuestStatus.DRAFT,
                experience_reward=ExperienceReward(50),
                start_date=date.today() + timedelta(days=1),
                due_date=date.today(),
            )

    def test_quest_completed_timestamp_validation(self):
        """Test that completed timestamp is only valid for completed quests"""
        with pytest.raises(
            ValueError, match="Completed timestamp only valid for completed quests"
        ):
            Quest(
                quest_id=QuestId(1),
                user_id=UserId(1),
                title=QuestTitle("Test Quest"),
                description=QuestDescription("Test"),
                difficulty=QuestDifficulty.EASY,
                quest_type=QuestType.MAIN,
                status=QuestStatus.ACTIVE,
                experience_reward=ExperienceReward(50),
                completed_at=datetime.utcnow(),
            )

    def test_daily_quest_cannot_be_paused(self):
        """Test that daily quests cannot be paused"""
        with pytest.raises(ValueError, match="Daily/Weekly quests cannot be paused"):
            Quest(
                quest_id=QuestId(1),
                user_id=UserId(1),
                title=QuestTitle("Daily Task"),
                description=QuestDescription("Test"),
                difficulty=QuestDifficulty.EASY,
                quest_type=QuestType.DAILY,
                status=QuestStatus.PAUSED,
                experience_reward=ExperienceReward(25),
            )

    def test_quest_status_transitions(self):
        """Test valid quest status transitions"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Test Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.DRAFT,
            experience_reward=ExperienceReward(100),
        )

        # Draft can transition to Active
        assert quest.can_transition_to(QuestStatus.ACTIVE)
        assert quest.can_transition_to(QuestStatus.FAILED)
        assert not quest.can_transition_to(QuestStatus.COMPLETED)
        assert not quest.can_transition_to(QuestStatus.PAUSED)

    def test_quest_activation(self):
        """Test quest activation"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Test Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.DRAFT,
            experience_reward=ExperienceReward(100),
        )

        quest.activate()

        assert quest.status == QuestStatus.ACTIVE
        assert quest.start_date == date.today()

    def test_quest_completion(self):
        """Test quest completion"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Test Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.MEDIUM,
            quest_type=QuestType.MAIN,
            status=QuestStatus.ACTIVE,
            experience_reward=ExperienceReward(100),
        )

        quest.complete()

        assert quest.status == QuestStatus.COMPLETED
        assert quest.completed_at is not None

    def test_quest_difficulty_multipliers(self):
        """Test quest difficulty experience multipliers"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Test Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.LEGENDARY,
            quest_type=QuestType.MAIN,
            status=QuestStatus.ACTIVE,
            experience_reward=ExperienceReward(100),
        )

        assert quest.get_difficulty_multiplier() == 3.0
        assert quest.calculate_final_experience() == 300

    def test_quest_overdue_detection(self):
        """Test quest overdue detection"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Overdue Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.EASY,
            quest_type=QuestType.MAIN,
            status=QuestStatus.ACTIVE,
            experience_reward=ExperienceReward(50),
            due_date=date.today() - timedelta(days=1),
        )

        assert quest.is_overdue()

    def test_completed_quest_not_overdue(self):
        """Test that completed quests are not considered overdue"""
        quest = Quest(
            quest_id=QuestId(1),
            user_id=UserId(1),
            title=QuestTitle("Completed Quest"),
            description=QuestDescription("Test"),
            difficulty=QuestDifficulty.EASY,
            quest_type=QuestType.MAIN,
            status=QuestStatus.COMPLETED,
            experience_reward=ExperienceReward(50),
            due_date=date.today() - timedelta(days=1),
            completed_at=datetime.utcnow(),
        )

        assert not quest.is_overdue()


class TestHabit:
    """Test Habit domain entity"""

    def test_habit_creation_with_valid_data(self):
        """Test creating a habit with valid data"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(5),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        assert habit.name.value == "Exercise"
        assert habit.frequency == HabitFrequency.DAILY
        assert habit.current_streak.value == 5

    def test_habit_streak_validation(self):
        """Test that current streak cannot exceed longest streak"""
        with pytest.raises(
            ValueError, match="Current streak cannot exceed longest streak"
        ):
            Habit(
                habit_id=HabitId(1),
                user_id=UserId(1),
                name=HabitName("Exercise"),
                description="Daily workout",
                frequency=HabitFrequency.DAILY,
                target_count=CompletionCount(1),
                current_streak=StreakCount(15),
                longest_streak=StreakCount(10),
                experience_reward=ExperienceReward(25),
            )

    def test_habit_streak_bonus_calculation(self):
        """Test habit streak bonus calculation"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(25),
            longest_streak=StreakCount(30),
            experience_reward=ExperienceReward(25),
        )

        # 25-day streak should give 1.5x bonus
        assert habit.calculate_streak_bonus() == 1.5
        assert habit.calculate_experience_reward() == 37  # 25 * 1.5 = 37.5 -> 37

    def test_habit_streak_update_consecutive(self):
        """Test habit streak update for consecutive completions"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(5),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        today = date.today()
        yesterday = today - timedelta(days=1)

        habit.update_streak(today, yesterday)

        assert habit.current_streak.value == 6

    def test_complete_habit_updates_state_and_returns_details(self):
        """Test completing a habit returns experience, streak, and milestone data"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(6),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        today = date.today()
        yesterday = today - timedelta(days=1)

        experience, streak, milestone = habit.complete_habit(
            completion_date=today,
            completion_count=1,
            previous_completion_date=yesterday,
        )

        assert experience == habit.calculate_experience_reward(1)
        assert streak.value == 7
        assert habit.current_streak.value == 7
        assert milestone == "week"

    def test_habit_streak_update_broken(self):
        """Test habit streak reset when broken"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(5),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        today = date.today()
        three_days_ago = today - timedelta(days=3)

        habit.update_streak(today, three_days_ago)

        assert habit.current_streak.value == 1  # Reset to 1

    def test_habit_longest_streak_update(self):
        """Test longest streak update when current exceeds it"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(9),
            longest_streak=StreakCount(10),
            experience_reward=ExperienceReward(25),
        )

        today = date.today()
        yesterday = today - timedelta(days=1)

        habit.update_streak(today, yesterday)

        assert habit.current_streak.value == 10
        assert habit.longest_streak.value == 10

        # One more day should update longest streak
        tomorrow = today + timedelta(days=1)
        habit.update_streak(tomorrow, today)

        assert habit.current_streak.value == 11
        assert habit.longest_streak.value == 11

    def test_habit_streak_milestones(self):
        """Test habit streak milestone detection"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(21),
            longest_streak=StreakCount(25),
            experience_reward=ExperienceReward(25),
        )

        assert habit.get_streak_milestone_type() == "habit_formation"

        habit.current_streak = StreakCount(100)
        assert habit.get_streak_milestone_type() == "mastery"

    def test_habit_break_streak(self):
        """Test manually breaking a habit streak"""
        habit = Habit(
            habit_id=HabitId(1),
            user_id=UserId(1),
            name=HabitName("Exercise"),
            description="Daily workout",
            frequency=HabitFrequency.DAILY,
            target_count=CompletionCount(1),
            current_streak=StreakCount(15),
            longest_streak=StreakCount(20),
            experience_reward=ExperienceReward(25),
        )

        habit.break_streak()

        assert habit.current_streak.value == 0


class TestHabitCompletion:
    """Test HabitCompletion domain entity"""

    def test_habit_completion_creation(self):
        """Test creating a habit completion"""
        completion = HabitCompletion(
            completion_id="test-id",
            habit_id=HabitId(1),
            count=CompletionCount(2),
            completion_date=date.today(),
            notes="Great workout!",
            experience_gained=ExperienceReward(50),
        )

        assert completion.habit_id.value == 1
        assert completion.count.value == 2
        assert completion.notes == "Great workout!"

    def test_habit_completion_id_generation(self):
        """Test automatic completion ID generation"""
        completion = HabitCompletion(
            completion_id="",
            habit_id=HabitId(1),
            count=CompletionCount(1),
            completion_date=date.today(),
            notes="",
            experience_gained=ExperienceReward(25),
        )

        # ID should be generated automatically
        assert completion.completion_id != ""
        assert len(completion.completion_id) > 0
