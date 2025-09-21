"""
Quests application services - use case orchestration and business workflows.
"""

from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from ..domain.entities import (
    Habit,
    HabitCompletion,
    HabitFrequency,
    Quest,
    QuestDifficulty,
    QuestStatus,
    QuestType,
)
from ..domain.repositories import (
    HabitCompletionRepository,
    HabitRepository,
    QuestRepository,
)
from ..domain.value_objects import (
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


def _generate_positive_identifier(modulus: int = 1_000_000_000_000) -> int:
    """Generate a positive integer identifier derived from a UUID."""

    raw_value = uuid4().int % modulus
    return raw_value if raw_value > 0 else 1


def _coerce_quest_id(quest_id: QuestId | int | str) -> QuestId:
    """Normalize incoming quest identifiers to QuestId value objects."""

    if isinstance(quest_id, QuestId):
        return quest_id

    try:
        quest_id_value = int(quest_id)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid quest_id: {quest_id}") from err

    return QuestId(quest_id_value)


def _coerce_user_id(user_id: UserId | int | str) -> UserId:
    """Normalize incoming user identifiers to UserId value objects."""

    if isinstance(user_id, UserId):
        return user_id

    try:
        user_id_value = int(user_id)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid user_id: {user_id}") from err

    return UserId(user_id_value)


def _coerce_habit_id(habit_id: HabitId | int | str) -> HabitId:
    """Normalize habit identifiers to HabitId value objects."""

    if isinstance(habit_id, HabitId):
        return habit_id

    try:
        habit_id_value = int(habit_id)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid habit_id: {habit_id}") from err

    return HabitId(habit_id_value)


class QuestService:
    """Service for quest management and workflows."""

    def __init__(self, quest_repo: QuestRepository):
        """
        Initialize the QuestService with a QuestRepository for persistence and retrieval operations.
        """
        self.quest_repo = quest_repo

    @staticmethod
    def _normalize_quest_id(quest_id: str | QuestId) -> QuestId:
        """Normalize incoming quest identifiers to QuestId value objects."""

        return _coerce_quest_id(quest_id)

    @staticmethod
    def _normalize_user_id(user_id: int | UserId | str) -> UserId:
        """Normalize incoming user identifiers to UserId value objects."""

        return _coerce_user_id(user_id)

    def create_quest(
        self,
        user_id: int | UserId,
        title: str,
        description: str = "",
        quest_type: QuestType = QuestType.MAIN,
        difficulty: str = "medium",
        experience_reward: int = 10,
        due_date: date | None = None,
    ) -> Quest:
        """
        Create and persist a new Quest for a user.

        Constructs a Quest entity from the provided fields, normalizes the `difficulty` string to
        the corresponding QuestDifficulty (falls back to MEDIUM), sets `created_at` and
        `updated_at` to the current UTC time, persists it via the repository, and returns the saved Quest.

        Parameters:
            user_id (int | UserId): Owner of the quest.
            title (str): Quest title.
            description (str): Optional quest description.
            quest_type (QuestType): Type/category of the quest.
            difficulty (str): Difficulty name (e.g., "easy", "medium", "hard"); mapped to QuestDifficulty.
        """
        if isinstance(difficulty, str):
            try:
                difficulty_enum = QuestDifficulty[difficulty.upper()]
            except KeyError:
                difficulty_enum = QuestDifficulty.MEDIUM
        else:
            difficulty_enum = difficulty
        quest_user_id = self._normalize_user_id(user_id)
        quest_title = title if isinstance(title, QuestTitle) else QuestTitle(title)
        quest_description = (
            description
            if isinstance(description, QuestDescription)
            else QuestDescription(description)
        )
        quest_experience = (
            experience_reward
            if isinstance(experience_reward, ExperienceReward)
            else ExperienceReward(experience_reward)
        )

        quest_type_enum = (
            quest_type if isinstance(quest_type, QuestType) else QuestType(quest_type)
        )

        quest = Quest(
            quest_id=QuestId(_generate_positive_identifier()),
            user_id=quest_user_id,
            title=quest_title,
            description=quest_description,
            quest_type=quest_type_enum,
            difficulty=difficulty_enum,
            status=QuestStatus.DRAFT,  # New quests start as draft
            experience_reward=quest_experience,
            due_date=due_date,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        return self.quest_repo.create(quest)

    def start_quest(self, quest_id: str) -> Quest:
        """
        Activate the quest identified by `quest_id` and persist the updated quest.

        Retrieves the quest from the repository, transitions it to its active state using the
        domain entity, saves the change, and returns the updated Quest.

        Raises:
            ValueError: If no quest with the given `quest_id` exists.

        Returns:
            Quest: The persisted quest after starting.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        quest.activate()
        return self.quest_repo.save(quest)

    def complete_quest(self, quest_id: str) -> tuple[Quest, int]:
        """
        Mark a quest as completed, persist the change, and return the updated quest plus the final experience awarded.

        The method retrieves the quest by id, invokes the domain completion logic on the Quest entity, saves the updated entity via the repository, and returns the saved Quest along with the final experience after any difficulty or bonus calculations.

        Parameters:
            quest_id (str): Identifier of the quest to complete.

        Returns:
            Tuple[Quest, int]: A tuple containing the saved Quest instance and the final experience points awarded.

        Raises:
            ValueError: If no quest exists with the given `quest_id`.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        quest.complete()
        updated_quest = self.quest_repo.save(quest)

        # Calculate final experience with difficulty bonus
        final_experience = quest.calculate_final_experience()

        return updated_quest, final_experience

    def update_quest_progress(self, quest_id: str, percentage: float) -> Quest:
        """
        Update the stored progress percentage for a quest and persist the change.

        Parameters:
            quest_id (str): Unique identifier of the quest to update.
            percentage (float): New progress value (expected as a percentage, e.g. 0.0–100.0).

        Returns:
            Quest: The updated and persisted Quest entity.

        Raises:
            ValueError: If no quest exists with the given `quest_id`.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        if not 0.0 <= percentage <= 100.0:
            raise ValueError("Quest progress must be between 0 and 100 percent")

        # The domain entity does not currently expose an explicit progress API. Persist the
        # provided value directly and update the timestamp so repositories can store the
        # change if they support a progress attribute.
        quest.progress = percentage
        quest.updated_at = datetime.now(timezone.utc)
        return self.quest_repo.save(quest)

    def pause_quest(self, quest_id: str) -> Quest:
        """
        Pause an active quest and persist the updated state.

        Pauses the quest identified by `quest_id` by delegating to the domain entity's `pause()`
        method and saves the updated quest.

        Parameters:
            quest_id (str): Identifier of the quest to pause.

        Returns:
            Quest: The persisted Quest with updated status.

        Raises:
            ValueError: If no quest with `quest_id` exists.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        quest.pause()
        return self.quest_repo.save(quest)

    def resume_quest(self, quest_id: str) -> Quest:
        """
        Resume a paused quest and persist the change.

        Delegates to the domain entity's `activate()` method, which enforces valid status
        transitions.

        Returns:
            Quest: The updated quest after resuming.

        Raises:
            ValueError: If no quest exists with the given quest_id.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        quest.activate()
        return self.quest_repo.save(quest)

    def fail_quest(self, quest_id: str, reason: str = "") -> Quest:
        """
        Mark the specified quest as failed and persist the change.

        Raises a ValueError if no quest with the given ID exists.

        The optional `reason` parameter is currently informational only; the domain entity
        does not persist failure reasons.

        Parameters:
            quest_id (str): ID of the quest to mark failed.
            reason (str): Optional reason for failing the quest.

        Returns:
            Quest: The updated Quest after being marked failed and saved.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest:
            raise ValueError(f"Quest {quest_identifier.value} not found")

        quest.fail()
        return self.quest_repo.save(quest)

    def get_user_quests(
        self,
        user_id: int | UserId,
        status: QuestStatus | None = None,
        quest_type: QuestType | None = None,
    ) -> list[Quest]:
        """Get quests for a user with optional filtering."""
        user_identifier = self._normalize_user_id(user_id)

        if status:
            return self.quest_repo.get_by_status(user_identifier, status)
        elif quest_type:
            return self.quest_repo.get_by_type(user_identifier, quest_type)
        else:
            return self.quest_repo.get_by_user_id(user_identifier)

    def get_overdue_quests(self, user_id: int | UserId) -> list[Quest]:
        """
        Return the list of overdue quests for the given user.

        Returns:
            List[Quest]: Quests whose due date has passed and are still not completed.
        """
        return self.quest_repo.get_overdue_quests(self._normalize_user_id(user_id))

    def get_upcoming_quests(self, user_id: int | UserId, days: int = 7) -> list[Quest]:
        """
        Return quests for the user that are due within the next `days` days (from today, inclusive).

        Parameters:
            user_id (int | UserId): ID of the user whose quests are requested.
            days (int): Number of days from today to look ahead (default 7).

        Returns:
            List[Quest]: Quests with due dates within the specified timeframe.
        """
        return self.quest_repo.get_due_soon(self._normalize_user_id(user_id), days)

    def delete_quest(self, quest_id: str) -> bool:
        """
        Delete a quest by its identifier.

        Parameters:
            quest_id (str): The ID of the quest to delete.

        Returns:
            bool: True if the quest was deleted, False if no quest was found.
        """
        quest_identifier = self._normalize_quest_id(quest_id)

        return self.quest_repo.delete(quest_identifier)

    def search_quests(
        self, user_id: int | UserId, query: str, limit: int = 20
    ) -> list[Quest]:
        """
        Search quests belonging to a user that match a text query.

        Parameters:
            user_id (int | UserId): ID of the user whose quests will be searched.
            query (str): Text to match against quest titles and descriptions.
            limit (int): Maximum number of results to return (default 20).

        Returns:
            List[Quest]: Quests matching the query for the specified user, up to `limit`.
        """
        return self.quest_repo.search_quests(
            self._normalize_user_id(user_id), query, limit
        )

    def get_quest_statistics(self, user_id: int | UserId) -> dict[str, Any]:
        """
        Return aggregated quest statistics for a user.

        Fetches all quests for the given user and computes counts and summary metrics.

        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - total_quests (int): Total number of quests for the user.
                - active_quests (int): Number of quests with status ACTIVE.
                - completed_quests (int): Number of quests with status COMPLETED.
                - failed_quests (int): Number of quests with status FAILED.
                - overdue_quests (int): Number of quests for which `is_overdue()` is True.
                - completion_rate (float): Percentage of quests completed (0–100). 0.0 if no quests.
                - total_experience_earned (int): Sum of `calculate_final_experience()` for completed quests.
                - average_completion_time (float): Placeholder numeric value for average completion time (currently always 0.0).
        """
        user_identifier = self._normalize_user_id(user_id)
        all_quests = self.quest_repo.get_by_user_id(user_identifier)

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
        """
        Initialize the HabitService with repository dependencies.

        Stores the habit and habit completion repository instances for use by the service.
        """
        self.habit_repo = habit_repo
        self.completion_repo = completion_repo

    @staticmethod
    def _normalize_user_id(user_id: int | UserId | str) -> UserId:
        """Normalize incoming user identifiers to UserId value objects."""

        return _coerce_user_id(user_id)

    @staticmethod
    def _normalize_habit_id(habit_id: HabitId | int | str) -> HabitId:
        """Normalize incoming habit identifiers to HabitId value objects."""

        return _coerce_habit_id(habit_id)

    def create_habit(
        self,
        user_id: int | UserId,
        name: str,
        description: str = "",
        frequency: HabitFrequency = HabitFrequency.DAILY,
        target_count: int = 1,
        experience_reward: int = 5,
    ) -> Habit:
        """
        Create and persist a new Habit for a user.

        Constructs a Habit entity with the provided fields, sets created_at/updated_at to the current UTC time, and saves it via the habit repository.

        Returns:
            Habit: The persisted Habit instance with any repository-assigned identifiers or metadata.
        """
        habit_user_id = self._normalize_user_id(user_id)
        habit_name = name if isinstance(name, HabitName) else HabitName(name)
        frequency_enum = (
            frequency
            if isinstance(frequency, HabitFrequency)
            else HabitFrequency(frequency)
        )
        habit_target = (
            target_count
            if isinstance(target_count, CompletionCount)
            else CompletionCount(target_count)
        )
        habit_experience = (
            experience_reward
            if isinstance(experience_reward, ExperienceReward)
            else ExperienceReward(experience_reward)
        )

        habit = Habit(
            habit_id=HabitId(_generate_positive_identifier()),
            user_id=habit_user_id,
            name=habit_name,
            description=description,
            frequency=frequency_enum,
            target_count=habit_target,
            current_streak=StreakCount(0),
            longest_streak=StreakCount(0),
            experience_reward=habit_experience,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return self.habit_repo.create(habit)

    def complete_habit(
        self,
        habit_id: HabitId | int | str,
        completion_date: date | None = None,
        count: int = 1,
        notes: str = "",
    ) -> tuple[Habit, HabitCompletion, int]:
        """
        Record a completion for a habit, update its streak, and persist both the habit and a HabitCompletion record.

        If completion_date is omitted, today's date (in the system local date) is used. Raises ValueError when the habit does not exist or a completion for the same habit and date already exists.

        Parameters:
            habit_id (HabitId | int | str): Identifier of the habit to complete.
            completion_date (date | None): Date of the completion; defaults to today when None.
            count (int): Number of times the habit was completed in this entry (defaults to 1).
            notes (str): Optional free-text notes attached to the completion.

        Returns:
            tuple(Habit, HabitCompletion, int): A 3-tuple containing the updated Habit entity, the persisted HabitCompletion record, and the experience points gained from this completion.
        """
        habit_identifier = self._normalize_habit_id(habit_id)

        habit = self.habit_repo.get_by_id(habit_identifier)
        if not habit:
            raise ValueError(f"Habit {habit_identifier.value} not found")

        if not completion_date:
            completion_date = date.today()

        # Check if already completed today
        existing_completion = self.completion_repo.get_completion_for_date(
            habit_identifier, completion_date
        )
        if existing_completion:
            raise ValueError(f"Habit already completed on {completion_date}")

        # Determine previous completion to maintain streak calculations
        previous_completion_date = None
        recent_completions = self.completion_repo.get_by_habit_id(
            habit_identifier, limit=1
        )
        if recent_completions:
            candidate_date = recent_completions[0].completion_date
            if candidate_date < completion_date:
                previous_completion_date = candidate_date

        # Complete the habit (updates streak)
        experience_gained, new_streak, milestone_reached = habit.complete_habit(
            completion_date=completion_date,
            completion_count=count,
            previous_completion_date=previous_completion_date,
        )

        # Save updated habit
        updated_habit = self.habit_repo.save(habit)

        # Create completion record
        user_identifier = (
            habit.user_id
            if isinstance(habit.user_id, UserId)
            else UserId(habit.user_id)
        )
        completion_count = (
            count if isinstance(count, CompletionCount) else CompletionCount(count)
        )
        completion_experience = (
            experience_gained
            if isinstance(experience_gained, ExperienceReward)
            else ExperienceReward(experience_gained)
        )
        streak_value = (
            new_streak
            if isinstance(new_streak, StreakCount)
            else StreakCount(new_streak)
        )

        completion = HabitCompletion(
            completion_id="",
            habit_id=habit_identifier,
            user_id=user_identifier,
            completion_date=completion_date,
            count=completion_count,
            notes=notes,
            experience_gained=completion_experience,
            streak_at_completion=streak_value,
            created_at=datetime.now(timezone.utc),
        )

        saved_completion = self.completion_repo.create(completion)

        return updated_habit, saved_completion, experience_gained

    def break_habit_streak(self, habit_id: HabitId | int | str) -> Habit:
        """
        Break the active streak for the specified habit and persist the change.

        This will reset the habit's streak state on the domain entity and save the updated habit via the repository.

        Returns:
            Habit: The saved Habit with its streak reset.

        Raises:
            ValueError: If no habit with the given `habit_id` exists.
        """
        habit_identifier = self._normalize_habit_id(habit_id)

        habit = self.habit_repo.get_by_id(habit_identifier)
        if not habit:
            raise ValueError(f"Habit {habit_identifier.value} not found")

        habit.break_streak()
        return self.habit_repo.save(habit)

    def get_user_habits(
        self, user_id: int | UserId, frequency: HabitFrequency | None = None
    ) -> list[Habit]:
        """Get habits for a user with optional frequency filter."""
        user_identifier = self._normalize_user_id(user_id)

        if frequency:
            return self.habit_repo.get_by_frequency(user_identifier, frequency)
        else:
            return self.habit_repo.get_by_user_id(user_identifier)

    def get_habits_due_today(self, user_id: int | UserId) -> list[Habit]:
        """Get habits due today for a user."""
        return self.habit_repo.get_due_today(self._normalize_user_id(user_id))

    def get_active_streaks(
        self, user_id: int | UserId, min_streak: int = 7
    ) -> list[Habit]:
        """
        Return the user's habits that currently have an active streak of at least `min_streak` days.

        Parameters:
            user_id (int | UserId): ID of the user whose habits to query.
            min_streak (int): Minimum consecutive days required to consider a streak active. Defaults to 7.

        Returns:
            List[Habit]: Habits belonging to the user with active streaks >= `min_streak`.
        """
        return self.habit_repo.get_active_streaks(
            self._normalize_user_id(user_id), min_streak
        )

    def get_habit_completions(
        self, habit_id: HabitId | int | str, limit: int = 30
    ) -> list[HabitCompletion]:
        """
        Return the most recent completions for a habit.

        Returns up to `limit` HabitCompletion records for `habit_id`, ordered newest first.
        """
        habit_identifier = self._normalize_habit_id(habit_id)
        return self.completion_repo.get_by_habit_id(habit_identifier, limit)

    def get_completion_history(
        self, habit_id: HabitId | int | str, start_date: date, end_date: date
    ) -> list[HabitCompletion]:
        """
        Return habit completions for the given habit between start_date and end_date.

        Retrieves all HabitCompletion records whose completion date falls within the provided date range.

        Parameters:
            habit_id (HabitId | int | str): ID of the habit to fetch completions for.
            start_date (date): Start of the date range.
            end_date (date): End of the date range.

        Returns:
            List[HabitCompletion]: List of completions in the specified date range.
        """
        habit_identifier = self._normalize_habit_id(habit_id)
        return self.completion_repo.get_by_date_range(
            habit_identifier, start_date, end_date
        )

    def delete_habit(self, habit_id: HabitId | int | str) -> bool:
        """
        Delete a habit by its ID.

        Parameters:
            habit_id (HabitId | int | str): Identifier of the habit to delete.

        Returns:
            bool: True if the habit was deleted, False if no habit with the given ID existed.
        """
        habit_identifier = self._normalize_habit_id(habit_id)
        return self.habit_repo.delete(habit_identifier)

    def delete_completion(self, completion_id: str) -> bool:
        """
        Delete a habit completion record.

        Parameters:
            completion_id (str): Identifier of the HabitCompletion to delete.

        Returns:
            bool: True if the completion was deleted, False if no record was found.
        """
        return self.completion_repo.delete_completion(completion_id)

    def search_habits(
        self, user_id: int | UserId, query: str, limit: int = 20
    ) -> list[Habit]:
        """
        Search a user's habits by text query.

        Performs a text search (e.g., name/description) scoped to the given user and returns up to `limit` matching Habit entities.

        Parameters:
            user_id (int | UserId): ID of the user whose habits will be searched.
            query (str): Search string to match against habit fields.
            limit (int): Maximum number of results to return (default 20).

        Returns:
            List[Habit]: Matching Habit objects, up to `limit`.
        """
        return self.habit_repo.search_habits(
            self._normalize_user_id(user_id), query, limit
        )

    def get_habit_statistics(
        self, user_id: int | UserId, days: int = 30
    ) -> dict[str, Any]:
        """
        Retrieve the user's habits and recent completion metrics (last `days` days) and return a summary dictionary containing counts and aggregated values.

        Parameters:
            user_id (int | UserId): The ID of the user whose statistics to retrieve.
            days (int, optional): Number of days to look back for completion statistics. Defaults to 30.

        Returns:
            dict: A dictionary containing the following keys:
                - total_habits (int): Total number of habits for the user.
                - active_streaks (int): Number of habits with a current streak > 0.
                - longest_streak (int): Longest streak among all habits.
                - daily_average (float): Average number of habit completions per day.
                - current_streak (int): Longest current streak across all habits.
                - streak_milestones (int): Number of habits whose current streak is at or above the 7-day milestone.
                - habits_due_today (int): Count of habits due today.
        """
        user_identifier = self._normalize_user_id(user_id)
        habits = self.habit_repo.get_by_user_id(user_identifier)
        completion_stats = self.completion_repo.get_completion_stats(
            user_identifier, days
        )

        stats = {
            "total_habits": len(habits),
            "active_streaks": len([h for h in habits if h.current_streak.value > 0]),
            "longest_streak": max((h.longest_streak.value for h in habits), default=0),
            "daily_average": completion_stats.get("daily_average", 0.0),
            "current_streak": completion_stats.get("current_streak", 0),
            "streak_milestones": len(
                [h for h in habits if h.current_streak.value >= 7]
            ),
            "habits_due_today": len(self.get_habits_due_today(user_identifier)),
        }

        return stats


class QuestChainService:
    """Service for managing quest chains and dependencies."""

    def __init__(self, quest_repo: QuestRepository):
        """
        Initialize the QuestService with a QuestRepository for persistence and retrieval operations.
        """
        self.quest_repo = quest_repo

    def create_quest_chain(
        self,
        user_id: int | UserId,
        parent_quest_id: QuestId | int | str,
        child_quests: list[dict[str, Any]],
    ) -> list[Quest]:
        """
        Create and persist a sequence of child quests linked to a parent quest.

        Creates Quest entities for each entry in `child_quests`, attaches the given `user_id`
        and `parent_quest_id`, sets `created_at`/`updated_at` timestamps, and persists them
        using the repository.

        Parameters:
            user_id (int | UserId): Owner of the quest chain.
            parent_quest_id (QuestId | int | str): Identifier of the parent quest.
            child_quests (List[Dict[str, Any]]): List of dicts containing fields for each child quest
                (e.g., title, description, quest_type, difficulty, experience_reward, due_date).
                Keys should match the Quest constructor except `user_id`, `parent_quest_id`,
                `created_at`, and `updated_at` which are provided by this method.

        Returns:
            List[Quest]: The list of persisted Quest instances for the created child quests.
        """
        created_quests: list[Quest] = []

        quest_user_id = user_id if isinstance(user_id, UserId) else UserId(user_id)
        parent_identifier = (
            None if parent_quest_id is None else str(parent_quest_id).strip() or None
        )

        for quest_data in child_quests:
            sanitized = self._sanitize_child_quest_data(quest_data)

            raw_identifier = sanitized.pop("quest_id")
            if isinstance(raw_identifier, QuestId):
                quest_identifier = raw_identifier
            elif raw_identifier is None:
                quest_identifier = QuestId(_generate_positive_identifier())
            else:
                try:
                    quest_identifier = QuestId(raw_identifier)
                except (TypeError, ValueError) as err:
                    raise ValueError(
                        f"Invalid quest_id value in quest chain payload: {raw_identifier}"
                    ) from err

            title_value = sanitized.pop("title")
            quest_title = (
                title_value
                if isinstance(title_value, QuestTitle)
                else QuestTitle(str(title_value).strip())
            )

            description_value = sanitized.pop("description")
            quest_description = (
                description_value
                if isinstance(description_value, QuestDescription)
                else QuestDescription(str(description_value).strip())
            )

            difficulty_value = sanitized.pop("difficulty", QuestDifficulty.MEDIUM)
            if isinstance(difficulty_value, str):
                difficulty_key = difficulty_value.upper()
                if difficulty_key not in QuestDifficulty.__members__:
                    raise ValueError(f"Invalid difficulty: {difficulty_value}")
                difficulty_value = QuestDifficulty[difficulty_key]

            quest_type_value = sanitized.pop("quest_type", QuestType.SIDE)
            if isinstance(quest_type_value, str):
                quest_type_key = quest_type_value.upper()
                quest_type_value = (
                    QuestType[quest_type_key]
                    if quest_type_key in QuestType.__members__
                    else QuestType.SIDE
                )

            status_value = sanitized.pop("status", QuestStatus.DRAFT)
            if isinstance(status_value, str):
                status_key = status_value.upper()
                status_value = (
                    QuestStatus[status_key]
                    if status_key in QuestStatus.__members__
                    else QuestStatus.DRAFT
                )

            experience_value = sanitized.pop("experience_reward", 0)
            if isinstance(experience_value, ExperienceReward):
                quest_experience = experience_value
            else:
                try:
                    quest_experience = ExperienceReward(int(experience_value))
                except (TypeError, ValueError) as err:
                    raise ValueError("experience_reward must be an integer") from err

            progress_value = sanitized.pop("progress", None)
            progress_amount = progress_value if progress_value is not None else 0.0
            timestamp = datetime.now(timezone.utc)

            prerequisite_values = sanitized.pop("prerequisite_quest_ids", None)
            prerequisite_ids = (
                prerequisite_values if prerequisite_values is not None else []
            )

            quest = Quest(
                quest_id=quest_identifier,
                user_id=quest_user_id,
                title=quest_title,
                description=quest_description,
                quest_type=quest_type_value,
                difficulty=difficulty_value,
                status=status_value,
                experience_reward=quest_experience,
                progress=progress_amount,
                start_date=sanitized.pop("start_date", None),
                due_date=sanitized.pop("due_date", None),
                completed_at=sanitized.pop("completed_at", None),
                prerequisite_quest_ids=prerequisite_ids,
                parent_quest_id=parent_identifier,
                created_at=timestamp,
                updated_at=timestamp,
            )

            if sanitized:
                # Defensive guard: _sanitize_child_quest_data should have consumed all keys.
                unexpected_keys = ", ".join(sorted(sanitized.keys()))
                raise ValueError(
                    f"Unsupported quest fields provided after sanitization: {unexpected_keys}"
                )

            if parent_quest_id is not None:
                quest.parent_quest_id = (
                    str(parent_quest_id.value)
                    if isinstance(parent_quest_id, QuestId)
                    else str(parent_quest_id)
                )
            created_quest = self.quest_repo.create(quest)
            created_quests.append(created_quest)

        return created_quests

    @staticmethod
    def _normalize_enum(value: Any, enum_cls: type, field_name: str):
        """Normalize raw enum values to the expected Enum instances."""

        if isinstance(value, enum_cls):
            return value

        if value is None:
            raise ValueError(f"{field_name} is required for quest creation.")

        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError(f"{field_name} cannot be blank.")
            try:
                return enum_cls(value)
            except ValueError:
                try:
                    return enum_cls[value.upper()]
                except KeyError as exc:
                    raise ValueError(f"Invalid {field_name}: {value}") from exc

        try:
            return enum_cls(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}: {value}") from exc

    @staticmethod
    def _normalize_progress(value: Any) -> float:
        """Ensure quest progress/completion values are floats within 0-100."""

        try:
            progress_value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("progress must be a numeric value") from exc

        if not 0.0 <= progress_value <= 100.0:
            raise ValueError("progress must be between 0 and 100")

        return progress_value

    @staticmethod
    def _normalize_date(value: Any, field_name: str) -> date:
        """Normalize date inputs from strings or datetime objects."""

        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError(f"{field_name} cannot be blank")
            try:
                return date.fromisoformat(value)
            except ValueError:
                try:
                    return datetime.fromisoformat(value).date()
                except ValueError as exc:
                    raise ValueError(
                        f"{field_name} must be an ISO formatted date string"
                    ) from exc

        raise ValueError(
            f"{field_name} must be a date, datetime, or ISO formatted string"
        )

    @staticmethod
    def _normalize_datetime(value: Any, field_name: str) -> datetime:
        """Normalize datetime inputs from strings or dates."""

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())

        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError(f"{field_name} cannot be blank")
            try:
                return datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(
                    f"{field_name} must be an ISO formatted datetime string"
                ) from exc

        raise ValueError(
            f"{field_name} must be a datetime or ISO formatted datetime string"
        )

    @staticmethod
    def _normalize_prerequisites(value: Any) -> list[str]:
        """Normalize prerequisite quest identifiers to a list of strings."""

        if value is None:
            return []

        if isinstance(value, str):
            return [value] if value.strip() else []

        if isinstance(value, list | tuple | set):
            return [str(item) for item in value if str(item).strip()]

        raise ValueError("prerequisite_quest_ids must be a sequence of quest IDs")

    def _sanitize_child_quest_data(self, quest_data: dict[str, Any]) -> dict[str, Any]:
        """Remove disallowed keys and normalize quest fields."""

        if not isinstance(quest_data, dict):
            raise ValueError("Each child quest must be provided as a dictionary")

        filtered_data = {
            key: value
            for key, value in quest_data.items()
            if key not in {"user_id", "parent_quest_id", "created_at", "updated_at"}
        }

        sanitized: dict[str, Any] = {}

        quest_id = filtered_data.pop("quest_id", None)
        if quest_id is None or not str(quest_id).strip():
            sanitized["quest_id"] = None
        else:
            sanitized["quest_id"] = str(quest_id).strip()

        title = filtered_data.pop("title", None)
        if title is None or not str(title).strip():
            raise ValueError("Child quests require a non-empty title")
        sanitized["title"] = str(title).strip()

        description = filtered_data.pop("description", "")
        sanitized["description"] = str(description)

        quest_type_value = filtered_data.pop("quest_type", QuestType.MAIN)
        sanitized["quest_type"] = self._normalize_enum(
            quest_type_value, QuestType, "quest_type"
        )

        difficulty_value = filtered_data.pop("difficulty", QuestDifficulty.MEDIUM)
        sanitized["difficulty"] = self._normalize_enum(
            difficulty_value, QuestDifficulty, "difficulty"
        )

        status_value = filtered_data.pop("status", QuestStatus.DRAFT)
        sanitized["status"] = self._normalize_enum(status_value, QuestStatus, "status")

        experience_reward = filtered_data.pop("experience_reward", None)
        if experience_reward is None:
            raise ValueError("Child quests require an experience_reward value")
        try:
            reward_value = int(experience_reward)
        except (TypeError, ValueError) as exc:
            raise ValueError("experience_reward must be an integer") from exc
        if reward_value < 0:
            raise ValueError("experience_reward cannot be negative")
        sanitized["experience_reward"] = reward_value

        progress_value = filtered_data.pop("progress", None)
        completion_percentage = filtered_data.pop("completion_percentage", None)
        progress_source = (
            progress_value if progress_value is not None else completion_percentage
        )
        if progress_source is not None:
            sanitized["progress"] = self._normalize_progress(progress_source)

        for date_field in ("start_date", "due_date"):
            if date_field in filtered_data:
                sanitized[date_field] = self._normalize_date(
                    filtered_data.pop(date_field), date_field
                )

        if "completed_at" in filtered_data:
            sanitized["completed_at"] = self._normalize_datetime(
                filtered_data.pop("completed_at"), "completed_at"
            )

        if "prerequisite_quest_ids" in filtered_data:
            sanitized["prerequisite_quest_ids"] = self._normalize_prerequisites(
                filtered_data.pop("prerequisite_quest_ids")
            )

        if filtered_data:
            raise ValueError(
                "Unsupported quest fields provided: "
                + ", ".join(sorted(filtered_data.keys()))
            )

        return sanitized

    def get_quest_chain(self, parent_quest_id: QuestId | int | str) -> list[Quest]:
        """
        Return all child quests that belong to the chain of the given parent quest.

        Returns an empty list if there are no child quests.
        """
        try:
            quest_identifier = _coerce_quest_id(parent_quest_id)
        except ValueError:
            return []
        return self.quest_repo.get_by_parent_quest(quest_identifier)

    def check_prerequisites(self, quest_id: QuestId | int | str) -> bool:
        """Check if all prerequisite quests are completed."""
        quest_identifier = _coerce_quest_id(quest_id)
        quest = self.quest_repo.get_by_id(quest_identifier)
        if not quest or not quest.prerequisite_quest_ids:
            return True

        for prereq_id in quest.prerequisite_quest_ids:
            try:
                prereq_identifier = _coerce_quest_id(prereq_id)
            except ValueError:
                return False
            prereq_quest = self.quest_repo.get_by_id(prereq_identifier)
            if not prereq_quest or prereq_quest.status != QuestStatus.COMPLETED:
                return False

        return True

    def unlock_next_quests(
        self, completed_quest_id: QuestId | int | str
    ) -> list[Quest]:
        """
        Unlock quests that list the given quest as a prerequisite.

        First fetches the completed quest to obtain its user_id, then searches that user's quests for any that:
        - includes completed_quest_id in its prerequisite_quest_ids,
        - is in QuestStatus.DRAFT, and
        - passes check_prerequisites(quest_id),

        the method sets the quest's status to QuestStatus.ACTIVE, persists the change via the repository, and collects the updated quest.

        Parameters:
            completed_quest_id (QuestId | int | str): ID of the quest that was completed.

        Returns:
            List[Quest]: the quests that were transitioned to ACTIVE and saved.

        Raises:
            ValueError: If the completed quest is not found.
        """
        # First, fetch the completed quest to get the user_id
        try:
            completed_identifier: QuestId | str = _coerce_quest_id(completed_quest_id)
        except ValueError:
            completed_identifier = str(completed_quest_id)

        completed_quest = self.quest_repo.get_by_id(completed_identifier)
        if not completed_quest:
            raise ValueError(f"Completed quest {completed_quest_id} not found")

        # Find quests for this user that have this quest as a prerequisite
        completed_user = completed_quest.user_id
        if not isinstance(completed_user, UserId):
            completed_user = _coerce_user_id(completed_user).value

        all_quests = self.quest_repo.get_by_user_id(completed_user)
        unlocked_quests = []
        completed_token = (
            str(completed_identifier.value)
            if isinstance(completed_identifier, QuestId)
            else str(completed_identifier)
        )

        for quest in all_quests:
            quest_identifier = quest.quest_id
            if quest_identifier is None:
                continue
            if (
                completed_token in quest.prerequisite_quest_ids
                and quest.status == QuestStatus.DRAFT
                and self.check_prerequisites(quest_identifier)
            ):
                quest.status = QuestStatus.ACTIVE
                updated_quest = self.quest_repo.save(quest)
                unlocked_quests.append(updated_quest)

        return unlocked_quests
