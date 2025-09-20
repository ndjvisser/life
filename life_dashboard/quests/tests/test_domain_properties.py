"""
Property-based tests for Quest domain using Hypothesis.

These tests generate random inputs to validate domain invariants and edge cases.
"""

from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from life_dashboard.quests.domain.entities import (
    Habit,
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


# Custom strategies for domain objects
@composite
def quest_ids(draw):
    """Generate valid quest IDs"""
    return QuestId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def user_ids(draw):
    """Generate valid user IDs"""
    return UserId(draw(st.integers(min_value=1, max_value=1000000)))


@composite
def quest_titles(draw):
    """Generate valid quest titles"""
    title = draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    return QuestTitle(title)


@composite
def quest_descriptions(draw):
    """Generate valid quest descriptions"""
    description = draw(st.text(max_size=2000))
    return QuestDescription(description)


@composite
def experience_rewards(draw):
    """Generate valid experience rewards"""
    return ExperienceReward(draw(st.integers(min_value=0, max_value=10000)))


@composite
def habit_names(draw):
    """Generate valid habit names"""
    name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    return HabitName(name)


@composite
def streak_counts(draw):
    """Generate valid streak counts"""
    return StreakCount(draw(st.integers(min_value=0, max_value=10000)))


@composite
def completion_counts(draw):
    """Generate valid completion counts"""
    return CompletionCount(draw(st.integers(min_value=0, max_value=1000)))


@composite
def valid_date_ranges(draw):
    """Generate valid start/end date pairs"""
    base_date = date.today()
    start_offset = draw(st.integers(min_value=-365, max_value=365))
    duration = draw(st.integers(min_value=1, max_value=365))

    start_date = base_date + timedelta(days=start_offset)
    end_date = start_date + timedelta(days=duration)

    return start_date, end_date


class TestQuestProperties:
    """Property-based tests for Quest entity"""

    @given(
        quest_id=quest_ids(),
        user_id=user_ids(),
        title=quest_titles(),
        description=quest_descriptions(),
        difficulty=st.sampled_from(QuestDifficulty),
        quest_type=st.sampled_from(QuestType),
        experience_reward=experience_rewards(),
    )
    def test_quest_creation_always_valid_with_valid_inputs(
        self,
        quest_id,
        user_id,
        title,
        description,
        difficulty,
        quest_type,
        experience_reward,
    ):
        """Test that quest creation always succeeds with valid inputs"""
        quest = Quest(
            quest_id=quest_id,
            user_id=user_id,
            title=title,
            description=description,
            difficulty=difficulty,
            quest_type=quest_type,
            status=QuestStatus.DRAFT,
            experience_reward=experience_reward,
        )

        assert quest.quest_id == quest_id
        assert quest.user_id == user_id
        assert quest.title == title
        assert quest.status == QuestStatus.DRAFT

    @given(
        quest_id=quest_ids(),
        user_id=user_ids(),
        title=quest_titles(),
        description=quest_descriptions(),
        difficulty=st.sampled_from(QuestDifficulty),
        quest_type=st.sampled_from(QuestType),
        experience_reward=experience_rewards(),
        date_range=valid_date_ranges(),
    )
    def test_quest_with_valid_date_range_always_succeeds(
        self,
        quest_id,
        user_id,
        title,
        description,
        difficulty,
        quest_type,
        experience_reward,
        date_range,
    ):
        """Test that quests with valid date ranges always succeed"""
        start_date, due_date = date_range

        quest = Quest(
            quest_id=quest_id,
            user_id=user_id,
            title=title,
            description=description,
            difficulty=difficulty,
            quest_type=quest_type,
            status=QuestStatus.DRAFT,
            experience_reward=experience_reward,
            start_date=start_date,
            due_date=due_date,
        )

        assert quest.start_date == start_date
        assert quest.due_date == due_date
        assert quest.start_date <= quest.due_date

    @given(
        quest_id=quest_ids(),
        user_id=user_ids(),
        title=quest_titles(),
        description=quest_descriptions(),
        difficulty=st.sampled_from(QuestDifficulty),
        quest_type=st.sampled_from(QuestType),
        experience_reward=experience_rewards(),
    )
    def test_quest_difficulty_multiplier_always_positive(
        self,
        quest_id,
        user_id,
        title,
        description,
        difficulty,
        quest_type,
        experience_reward,
    ):
        """Test that difficulty multipliers are always positive"""
        quest = Quest(
            quest_id=quest_id,
            user_id=user_id,
            title=title,
            description=description,
            difficulty=difficulty,
            quest_type=quest_type,
            status=QuestStatus.DRAFT,
            experience_reward=experience_reward,
        )

        multiplier = quest.get_difficulty_multiplier()
        final_experience = quest.calculate_final_experience()

        assert multiplier > 0
        assert final_experience >= 0
        assert final_experience == int(experience_reward.value * multiplier)

    @given(
        quest_id=quest_ids(),
        user_id=user_ids(),
        title=quest_titles(),
        description=quest_descriptions(),
        difficulty=st.sampled_from(QuestDifficulty),
        quest_type=st.sampled_from(QuestType),
        experience_reward=experience_rewards(),
    )
    def test_quest_status_transitions_are_deterministic(
        self,
        quest_id,
        user_id,
        title,
        description,
        difficulty,
        quest_type,
        experience_reward,
    ):
        """Test that quest status transitions are deterministic"""
        quest = Quest(
            quest_id=quest_id,
            user_id=user_id,
            title=title,
            description=description,
            difficulty=difficulty,
            quest_type=quest_type,
            status=QuestStatus.DRAFT,
            experience_reward=experience_reward,
        )

        # Draft state should always allow activation
        assert quest.can_transition_to(QuestStatus.ACTIVE)

        # Activate quest
        quest.activate()
        assert quest.status == QuestStatus.ACTIVE

        # Active state should allow completion
        assert quest.can_transition_to(QuestStatus.COMPLETED)

        # Complete quest
        quest.complete()
        assert quest.status == QuestStatus.COMPLETED

        # Completed state should not allow any transitions
        assert not quest.can_transition_to(QuestStatus.ACTIVE)
        assert not quest.can_transition_to(QuestStatus.FAILED)
        assert not quest.can_transition_to(QuestStatus.PAUSED)


class TestHabitProperties:
    """Property-based tests for Habit entity"""

    @given(
        habit_id=st.integers(min_value=1, max_value=1000000).map(HabitId),
        user_id=user_ids(),
        name=habit_names(),
        description=st.text(max_size=500),
        frequency=st.sampled_from(HabitFrequency),
        target_count=completion_counts(),
        current_streak=streak_counts(),
        experience_reward=experience_rewards(),
    )
    def test_habit_creation_with_valid_streaks(
        self,
        habit_id,
        user_id,
        name,
        description,
        frequency,
        target_count,
        current_streak,
        experience_reward,
    ):
        """Test habit creation with valid streak relationships"""
        # Ensure longest streak is at least as long as current streak, but within limits
        longest_streak_value = min(
            10000, max(current_streak.value, current_streak.value + 10)
        )
        longest_streak = StreakCount(longest_streak_value)

        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency,
            target_count=target_count,
            current_streak=current_streak,
            longest_streak=longest_streak,
            experience_reward=experience_reward,
        )

        assert habit.current_streak.value <= habit.longest_streak.value

    @given(
        habit_id=st.integers(min_value=1, max_value=1000000).map(HabitId),
        user_id=user_ids(),
        name=habit_names(),
        description=st.text(max_size=500),
        frequency=st.sampled_from(HabitFrequency),
        target_count=completion_counts(),
        current_streak=streak_counts(),
        experience_reward=experience_rewards(),
        completion_count=st.integers(min_value=1, max_value=10),
    )
    def test_habit_experience_calculation_always_positive(
        self,
        habit_id,
        user_id,
        name,
        description,
        frequency,
        target_count,
        current_streak,
        experience_reward,
        completion_count,
    ):
        """Test that habit experience calculation is always positive"""
        longest_streak_value = min(
            10000, max(current_streak.value, current_streak.value + 10)
        )
        longest_streak = StreakCount(longest_streak_value)

        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency,
            target_count=target_count,
            current_streak=current_streak,
            longest_streak=longest_streak,
            experience_reward=experience_reward,
        )

        experience = habit.calculate_experience_reward(completion_count)
        streak_bonus = habit.calculate_streak_bonus()

        assert experience >= 0
        assert streak_bonus >= 1.0
        assert experience == int(
            experience_reward.value * completion_count * streak_bonus
        )

    @given(
        habit_id=st.integers(min_value=1, max_value=1000000).map(HabitId),
        user_id=user_ids(),
        name=habit_names(),
        description=st.text(max_size=500),
        frequency=st.sampled_from(HabitFrequency),
        target_count=completion_counts(),
        current_streak=streak_counts(),
        experience_reward=experience_rewards(),
    )
    def test_habit_streak_bonus_increases_with_streak(
        self,
        habit_id,
        user_id,
        name,
        description,
        frequency,
        target_count,
        current_streak,
        experience_reward,
    ):
        """Test that streak bonus increases with longer streaks"""
        longest_streak_value = min(
            10000, max(current_streak.value, current_streak.value + 10)
        )
        longest_streak = StreakCount(longest_streak_value)

        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency,
            target_count=target_count,
            current_streak=current_streak,
            longest_streak=longest_streak,
            experience_reward=experience_reward,
        )

        initial_bonus = habit.calculate_streak_bonus()

        # Increase streak and check bonus
        if current_streak.value < 10000:  # Avoid overflow
            habit.current_streak = StreakCount(current_streak.value + 50)
            new_bonus = habit.calculate_streak_bonus()

            # Bonus should be greater or equal (never decrease)
            assert new_bonus >= initial_bonus

    @given(
        habit_id=st.integers(min_value=1, max_value=1000000).map(HabitId),
        user_id=user_ids(),
        name=habit_names(),
        description=st.text(max_size=500),
        frequency=st.sampled_from(HabitFrequency),
        target_count=completion_counts(),
        current_streak=streak_counts(),
        experience_reward=experience_rewards(),
    )
    def test_habit_break_streak_resets_to_zero(
        self,
        habit_id,
        user_id,
        name,
        description,
        frequency,
        target_count,
        current_streak,
        experience_reward,
    ):
        """Test that breaking streak always resets to zero"""
        longest_streak_value = min(
            10000, max(current_streak.value, current_streak.value + 10)
        )
        longest_streak = StreakCount(longest_streak_value)

        habit = Habit(
            habit_id=habit_id,
            user_id=user_id,
            name=name,
            description=description,
            frequency=frequency,
            target_count=target_count,
            current_streak=current_streak,
            longest_streak=longest_streak,
            experience_reward=experience_reward,
        )

        habit.break_streak()

        assert habit.current_streak.value == 0
        # Longest streak should remain unchanged
        assert habit.longest_streak.value == longest_streak.value


class TestValueObjectProperties:
    """Property-based tests for value objects"""

    @given(st.integers(min_value=1, max_value=1000000))
    def test_quest_id_always_positive(self, value):
        """Test that QuestId always accepts positive values"""
        quest_id = QuestId(value)
        assert quest_id.value == value
        assert quest_id.value > 0

    @given(st.integers(max_value=0))
    def test_quest_id_rejects_non_positive(self, value):
        """Test that QuestId rejects non-positive values"""
        with pytest.raises(ValueError):
            QuestId(value)

    @given(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    def test_quest_title_accepts_valid_strings(self, title):
        """Test that QuestTitle accepts valid strings"""
        quest_title = QuestTitle(title)
        assert quest_title.value == title

    @given(st.text(min_size=201))
    def test_quest_title_rejects_long_strings(self, title):
        """Test that QuestTitle rejects strings over 200 characters"""
        with pytest.raises(ValueError):
            QuestTitle(title)

    @given(st.integers(min_value=0, max_value=10000))
    def test_experience_reward_accepts_valid_range(self, value):
        """Test that ExperienceReward accepts valid range"""
        reward = ExperienceReward(value)
        assert reward.value == value
        assert 0 <= reward.value <= 10000

    @given(st.integers(min_value=10001))
    def test_experience_reward_rejects_excessive_values(self, value):
        """Test that ExperienceReward rejects excessive values"""
        with pytest.raises(ValueError):
            ExperienceReward(value)

    @given(st.integers(min_value=0, max_value=10000))
    def test_streak_count_accepts_valid_range(self, value):
        """Test that StreakCount accepts valid range"""
        streak = StreakCount(value)
        assert streak.value == value
        assert 0 <= streak.value <= 10000

    @given(st.integers(max_value=-1))
    def test_streak_count_rejects_negative(self, value):
        """Test that StreakCount rejects negative values"""
        with pytest.raises(ValueError):
            StreakCount(value)
