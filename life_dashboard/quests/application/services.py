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
        """
        Initialize the QuestService with a QuestRepository for persistence and retrieval operations.
        """
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
        """
        Create and persist a new Quest for a user.
        
        Constructs a Quest entity from the provided fields, normalizes the `difficulty` string to
        the corresponding Quest.QuestDifficulty (falls back to MEDIUM), sets `created_at` and
        `updated_at` to the current UTC time, persists it via the repository, and returns the saved Quest.
        
        Parameters:
            user_id (int): Owner of the quest.
            title (str): Quest title.
            description (str): Optional quest description.
            quest_type (QuestType): Type/category of the quest.
            difficulty (str): Difficulty name (e.g., "easy", "medium", "hard"); mapped to Quest.QuestDifficulty.
            experience_reward (int): Experience awarded on completion.
            due_date (Optional[date]): Optional due date for the quest.
        
        Returns:
            Quest: The persisted Quest entity with repository-assigned identifiers/timestamps.
        """
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
        """
        Start the quest identified by `quest_id` and persist the updated quest.
        
        Retrieves the quest from the repository, transitions it to its started state, saves the change, and returns the updated Quest.
        
        Raises:
            ValueError: If no quest with the given `quest_id` exists.
        
        Returns:
            Quest: The persisted quest after starting.
        """
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.start_quest()
        return self.quest_repo.save(quest)

    def complete_quest(self, quest_id: str) -> Tuple[Quest, int]:
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
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        experience_reward, completion_time = quest.complete_quest()
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
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.update_progress(percentage)
        return self.quest_repo.save(quest)

    def pause_quest(self, quest_id: str) -> Quest:
        """
        Pause an active quest and persist the updated state.
        
        Pauses the quest identified by `quest_id` by delegating to the domain entity's `pause_quest()` and saves the updated quest.
        
        Parameters:
            quest_id (str): Identifier of the quest to pause.
        
        Returns:
            Quest: The persisted Quest with updated status.
        
        Raises:
            ValueError: If no quest with `quest_id` exists.
        """
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.pause_quest()
        return self.quest_repo.save(quest)

    def resume_quest(self, quest_id: str) -> Quest:
        """
        Resume a paused quest and persist the change.
        
        Returns:
            Quest: The updated quest after resuming.
        
        Raises:
            ValueError: If no quest exists with the given quest_id.
        """
        quest = self.quest_repo.get_by_id(quest_id)
        if not quest:
            raise ValueError(f"Quest {quest_id} not found")

        quest.resume_quest()
        return self.quest_repo.save(quest)

    def fail_quest(self, quest_id: str, reason: str = "") -> Quest:
        """
        Mark the specified quest as failed and persist the change.
        
        Raises a ValueError if no quest with the given ID exists.
        
        Parameters:
            quest_id (str): ID of the quest to mark failed.
            reason (str): Optional reason for failing the quest.
        
        Returns:
            Quest: The updated Quest after being marked failed and saved.
        """
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
        """
        Return the list of overdue quests for the given user.
        
        Returns:
            List[Quest]: Quests whose due date has passed and are still not completed.
        """
        return self.quest_repo.get_overdue_quests(user_id)

    def get_upcoming_quests(self, user_id: int, days: int = 7) -> List[Quest]:
        """
        Return quests for the user that are due within the next `days` days (from today, inclusive).
        
        Parameters:
            user_id (int): ID of the user whose quests are requested.
            days (int): Number of days from today to look ahead (default 7).
        
        Returns:
            List[Quest]: Quests with due dates within the specified timeframe.
        """
        return self.quest_repo.get_due_soon(user_id, days)

    def delete_quest(self, quest_id: str) -> bool:
        """
        Delete a quest by its identifier.
        
        Parameters:
            quest_id (str): The ID of the quest to delete.
        
        Returns:
            bool: True if the quest was deleted, False if no quest was found.
        """
        return self.quest_repo.delete(quest_id)

    def search_quests(self, user_id: int, query: str, limit: int = 20) -> List[Quest]:
        """
        Search quests belonging to a user that match a text query.
        
        Parameters:
            user_id (int): ID of the user whose quests will be searched.
            query (str): Text to match against quest titles and descriptions.
            limit (int): Maximum number of results to return (default 20).
        
        Returns:
            List[Quest]: Quests matching the query for the specified user, up to `limit`.
        """
        return self.quest_repo.search_quests(user_id, query, limit)

    def get_quest_statistics(self, user_id: int) -> Dict[str, Any]:
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
        """
        Initialize the HabitService with repository dependencies.
        
        Stores the habit and habit completion repository instances for use by the service.
        """
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
        """
        Create and persist a new Habit for a user.
        
        Constructs a Habit entity with the provided fields, sets created_at/updated_at to the current UTC time, and saves it via the habit repository.
        
        Returns:
            Habit: The persisted Habit instance with any repository-assigned identifiers or metadata.
        """
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
        Record a completion for a habit, update its streak, and persist both the habit and a HabitCompletion record.
        
        If completion_date is omitted, today's date (in the system local date) is used. Raises ValueError when the habit does not exist or a completion for the same habit and date already exists.
        
        Parameters:
            habit_id (str): Identifier of the habit to complete.
            completion_date (date | None): Date of the completion; defaults to today when None.
            count (int): Number of times the habit was completed in this entry (defaults to 1).
            notes (str): Optional free-text notes attached to the completion.
        
        Returns:
            tuple(Habit, HabitCompletion, int): A 3-tuple containing the updated Habit entity, the persisted HabitCompletion record, and the experience points gained from this completion.
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
        """
        Break the active streak for the specified habit and persist the change.
        
        This will reset the habit's streak state on the domain entity and save the updated habit via the repository.
        
        Returns:
            Habit: The saved Habit with its streak reset.
        
        Raises:
            ValueError: If no habit with the given `habit_id` exists.
        """
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
        """
        Return the user's habits that currently have an active streak of at least `min_streak` days.
        
        Parameters:
            user_id (int): ID of the user whose habits to query.
            min_streak (int): Minimum consecutive days required to consider a streak active. Defaults to 7.
        
        Returns:
            List[Habit]: Habits belonging to the user with active streaks >= `min_streak`.
        """
        return self.habit_repo.get_active_streaks(user_id, min_streak)

    def get_habit_completions(
        self, habit_id: str, limit: int = 30
    ) -> List[HabitCompletion]:
        """
        Return the most recent completions for a habit.
        
        Returns up to `limit` HabitCompletion records for `habit_id`, ordered newest first.
        """
        return self.completion_repo.get_by_habit_id(habit_id, limit)

    def get_completion_history(
        self, habit_id: str, start_date: date, end_date: date
    ) -> List[HabitCompletion]:
        """
        Return habit completions for the given habit between start_date and end_date.
        
        Retrieves all HabitCompletion records whose completion date falls within the provided date range.
        
        Parameters:
            habit_id (str): ID of the habit to fetch completions for.
            start_date (date): Start of the date range.
            end_date (date): End of the date range.
        
        Returns:
            List[HabitCompletion]: List of completions in the specified date range.
        """
        return self.completion_repo.get_by_date_range(habit_id, start_date, end_date)

    def delete_habit(self, habit_id: str) -> bool:
        """
        Delete a habit by its ID.
        
        Parameters:
            habit_id (str): Identifier of the habit to delete.
        
        Returns:
            bool: True if the habit was deleted, False if no habit with the given ID existed.
        """
        return self.habit_repo.delete(habit_id)

    def delete_completion(self, completion_id: str) -> bool:
        """
        Delete a habit completion record.
        
        Parameters:
            completion_id (str): Identifier of the HabitCompletion to delete.
        
        Returns:
            bool: True if the completion was deleted, False if no record was found.
        """
        return self.completion_repo.delete_completion(completion_id)

    def search_habits(self, user_id: int, query: str, limit: int = 20) -> List[Habit]:
        """
        Search a user's habits by text query.
        
        Performs a text search (e.g., name/description) scoped to the given user and returns up to `limit` matching Habit entities.
        
        Parameters:
            user_id (int): ID of the user whose habits will be searched.
            query (str): Search string to match against habit fields.
            limit (int): Maximum number of results to return (default 20).
        
        Returns:
            List[Habit]: Matching Habit objects, up to `limit`.
        """
        return self.habit_repo.search_habits(user_id, query, limit)

    def get_habit_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Return aggregated habit statistics for a user.
        
        Retrieve the user's habits and recent completion metrics (last `days` days) and return a summary dictionary containing counts and aggregated values.
        
        Parameters:
            user_id (int): ID of the user to compute statistics for.
            days (int): Lookback window in days used when computing completion-related metrics (default 30).
        
        Returns:
            Dict[str, Any]: A stats dictionary with these keys:
                - total_habits (int): Total number of habits for the user.
                - active_streaks (int): Number of habits with a current streak greater than zero.
                - longest_streak (int): The longest streak among the user's habits.
                - total_completions (int): Total completions in the given lookback window.
                - completion_rate (float): Completion rate (percentage or fraction as provided by the completion repository).
                - total_experience_earned (int): Total experience gained from completions in the lookback window.
                - streak_milestones (int): Number of habits whose current streak is at or above the 7-day milestone.
                - habits_due_today (int): Count of habits due today.
        """
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
        """
        Initialize the QuestService with a QuestRepository for persistence and retrieval operations.
        """
        self.quest_repo = quest_repo

    def create_quest_chain(
        self, user_id: int, parent_quest_id: str, child_quests: List[Dict[str, Any]]
    ) -> List[Quest]:
        """
        Create and persist a sequence of child quests linked to a parent quest.
        
        Creates Quest entities for each entry in `child_quests`, attaches the given `user_id`
        and `parent_quest_id`, sets `created_at`/`updated_at` timestamps, and persists them
        using the repository.
        
        Parameters:
            child_quests (List[Dict[str, Any]]): List of dicts containing fields for each child quest
                (e.g., title, description, quest_type, difficulty, experience_reward, due_date).
                Keys should match the Quest constructor except `user_id`, `parent_quest_id`,
                `created_at`, and `updated_at` which are provided by this method.
        
        Returns:
            List[Quest]: The list of persisted Quest instances for the created child quests.
        """
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
        """
        Return all child quests that belong to the chain of the given parent quest.
        
        Returns an empty list if there are no child quests.
        """
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
        """
        Unlock quests that list the given quest as a prerequisite.
        
        Searches all quests (currently fetched with a placeholder user_id=0), and for each quest that:
        - includes completed_quest_id in its prerequisite_quest_ids,
        - is in QuestStatus.DRAFT, and
        - passes check_prerequisites(quest_id),
        
        the method sets the quest's status to QuestStatus.ACTIVE, persists the change via the repository, and collects the updated quest.
        
        Returns:
            List[Quest]: the quests that were transitioned to ACTIVE and saved.
        
        Note:
            The current implementation fetches quests using user_id=0 as a placeholder; in production this should query the real user scope.
        """
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
