"""
Quests infrastructure repositories - Django ORM implementations.
"""

from datetime import date, timedelta
from typing import Any

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
        """
        Convert a DjangoQuest model instance into a DomainQuest entity.

        Maps model fields to the domain object (id, user id, title, description, type, difficulty, status,
        experience_reward, start/start/due/completion timestamps, parent quest id, created/updated timestamps).
        Sets `completion_percentage` to 0.0 and `prerequisite_quest_ids` to an empty list because those
        values are not stored on the Django model.
        """
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
            parent_quest_id=getattr(django_quest, "parent_quest_id", None),
            prerequisite_quest_ids=[],  # Not in current model
            created_at=django_quest.created_at,
            updated_at=django_quest.updated_at,
        )

    def _from_domain(
        self, domain_quest: DomainQuest, django_quest: DjangoQuest | None = None
    ) -> DjangoQuest:
        """
        Create or update a DjangoQuest model instance from a DomainQuest.

        If `django_quest` is None a new DjangoQuest is instantiated and associated with the User identified by `domain_quest.user_id`. Fields copied from the domain entity: title, description, quest_type, difficulty, status, experience_reward, start_date, due_date, completed_at. If `domain_quest.updated_at` is provided, it will be written to the model's `updated_at`.

        Parameters:
            domain_quest (DomainQuest): Domain entity to convert.
            django_quest (Optional[DjangoQuest]): Existing model to update; if omitted a new instance is created.

        Returns:
            DjangoQuest: The updated or newly created Django model instance (not saved to the database).

        Raises:
            User.DoesNotExist: If creating a new DjangoQuest and no User exists with `domain_quest.user_id`.
        """
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

    def get_by_id(self, quest_id: str) -> DomainQuest | None:
        """
        Retrieve a DomainQuest by its string ID.

        Converts the provided quest_id to an integer and returns the corresponding DomainQuest, or None if the ID is invalid or no matching DjangoQuest exists.
        """
        try:
            django_quest = DjangoQuest.objects.select_related("user").get(
                id=int(quest_id)
            )
            return self._to_domain(django_quest)
        except (DjangoQuest.DoesNotExist, ValueError):
            return None

    def get_by_user_id(self, user_id: int) -> list[DomainQuest]:
        """
        Return all quests belonging to the given user as DomainQuest objects.

        Results are ordered by creation time descending (newest first). Returns an empty list if the user has no quests.
        """
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_status(self, user_id: int, status: QuestStatus) -> list[DomainQuest]:
        """
        Return a list of DomainQuest objects for a user filtered by quest status.

        Results are ordered by creation time descending. `status` is a QuestStatus enum value.
        Parameters:
            user_id (int): ID of the user whose quests to query.
            status (QuestStatus): Quest status to filter by.

        Returns:
            List[DomainQuest]: Matching quests converted to domain entities.
        """
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id, status=status.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_type(self, user_id: int, quest_type: QuestType) -> list[DomainQuest]:
        """Get quests by type for a user."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=user_id, quest_type=quest_type.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def save(self, quest: DomainQuest) -> DomainQuest:
        """
        Save an existing DomainQuest to the database and return the saved DomainQuest.

        The function looks up the corresponding DjangoQuest by quest.quest_id, updates its fields from
        the domain object, saves the model, and converts the saved model back to a DomainQuest.

        Parameters:
            quest (DomainQuest): Domain entity to persist. Must contain a valid `quest_id` for an existing record.

        Returns:
            DomainQuest: The updated domain entity reflecting values saved in the database.

        Raises:
            ValueError: If the provided `quest.quest_id` is invalid or no matching quest exists.
        """
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
        """
        Create and persist a new quest from a domain entity.

        Converts the provided DomainQuest into a Django model, saves it to the database,
        updates the input DomainQuest.quest_id with the generated database ID, and returns
        a fresh DomainQuest built from the saved model.

        Parameters:
            quest (DomainQuest): Domain representation of the quest to create. Its
                quest_id will be overwritten with the new database ID.

        Returns:
            DomainQuest: Domain representation of the newly created and persisted quest.
        """
        django_quest = self._from_domain(quest)
        django_quest.save()
        # Update quest_id with the generated ID
        quest.quest_id = str(django_quest.id)
        return self._to_domain(django_quest)

    def delete(self, quest_id: str) -> bool:
        """
        Delete a quest by its ID.

        Attempts to delete the DjangoQuest with the given string `quest_id` (expected to be an integer string).
        Returns True if the quest was found and deleted; returns False if the id is invalid or no matching quest exists.
        """
        try:
            DjangoQuest.objects.get(id=int(quest_id)).delete()
            return True
        except (DjangoQuest.DoesNotExist, ValueError):
            return False

    def get_overdue_quests(self, user_id: int) -> list[DomainQuest]:
        """
        Return the user's quests that are past their due date.

        Filters quests belonging to the given user with due_date < today and status in ("active", "paused"), ordered by due_date ascending. Returns a list of DomainQuest objects representing those overdue quests.
        """
        today = date.today()
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(
                user_id=user_id, due_date__lt=today, status__in=["active", "paused"]
            )
            .order_by("due_date")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_due_soon(self, user_id: int, days: int = 7) -> list[DomainQuest]:
        """
        Return active quests for a user with due dates from today up to (and including) today + days.

        Args:
            user_id (int): Primary key of the user whose quests are queried.
            days (int): Number of days from today to include (inclusive). Defaults to 7.

        Returns:
            List[DomainQuest]: DomainQuest objects ordered by due_date.
        """
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

    def get_by_parent_quest(self, parent_quest_id: str) -> list[DomainQuest]:
        """
        Return child DomainQuest objects for a given parent quest ID.

        Retrieves DjangoQuest rows with parent_quest_id equal to the provided ID, converts them to domain entities and returns them ordered by creation time (oldest first). If parent_quest_id is not a valid integer, an empty list is returned.

        Parameters:
            parent_quest_id (str): Parent quest identifier (string form of the Django PK).

        Returns:
            List[DomainQuest]: Child quests ordered by created_at; empty list on invalid id or no children.
        """
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
    ) -> list[DomainQuest]:
        """
        Search quests for a user by title or description (case-insensitive).

        Performs a partial, case-insensitive match against `title` and `description` for the specified user, orders results by `created_at` descending, and returns up to `limit` DomainQuest instances.

        Parameters:
            user_id (int): ID of the user whose quests will be searched.
            query (str): Substring to search for in titles and descriptions (uses `icontains`).
            limit (int): Maximum number of results to return (default 20).

        Returns:
            List[DomainQuest]: Matching quests converted to domain objects, ordered newest first.
        """
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
        """
        Convert a DjangoHabit model instance into a DomainHabit entity.

        Maps model fields to the domain object, including:
        - id -> habit_id (string)
        - user.id -> user_id
        - name, description, target_count, current_streak, longest_streak, experience_reward, created_at, updated_at
        - frequency -> HabitFrequency(enum)
        - last_practiced -> last_completed

        Parameters:
            django_habit (DjangoHabit): The Django model instance to convert.

        Returns:
            DomainHabit: The corresponding domain entity.
        """
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
            last_completed=None,  # Field removed from model
        )

    def _from_domain(
        self, domain_habit: DomainHabit, django_habit: DjangoHabit | None = None
    ) -> DjangoHabit:
        """
        Builds or updates a DjangoHabit model from a DomainHabit entity.

        If `django_habit` is not provided, the function fetches the User by `domain_habit.user_id`
        and constructs a new DjangoHabit instance attached to that user. Fields copied from the
        domain object include: name, description, frequency (uses the enum's `.value`), target_count,
        current_streak, longest_streak, experience_reward, and last_practiced (from `last_completed`).
        If `domain_habit.updated_at` is present, it is applied to the model.

        Returns:
            DjangoHabit: The created or updated Django model instance (not saved to the database).
        """
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

    def get_by_id(self, habit_id: str) -> DomainHabit | None:
        """
        Retrieve a DomainHabit by its ID.

        If the habit exists, returns the corresponding DomainHabit; returns None when the ID is invalid (non-integer) or no matching habit is found.

        Parameters:
            habit_id (str): Habit ID as a string (expected to be convertible to an integer).

        Returns:
            Optional[DomainHabit]: The habit domain object or None if not found or the id is invalid.
        """
        try:
            django_habit = DjangoHabit.objects.select_related("user").get(
                id=int(habit_id)
            )
            return self._to_domain(django_habit)
        except (DjangoHabit.DoesNotExist, ValueError):
            return None

    def get_by_user_id(self, user_id: int) -> list[DomainHabit]:
        """Get all habits for a user."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id)
            .order_by("-created_at")
        )
        return [self._to_domain(h) for h in django_habits]

    def get_by_frequency(
        self, user_id: int, frequency: HabitFrequency
    ) -> list[DomainHabit]:
        """
        Return the user's habits that match a given frequency.

        Filters Habit records for the provided user by the given HabitFrequency (uses the enum's .value),
        orders results by created_at descending, and converts each Django model to a DomainHabit.

        Parameters:
            user_id (int): ID of the user whose habits to query.
            frequency (HabitFrequency): Frequency enum used to filter habits.

        Returns:
            List[DomainHabit]: Matching habits as domain entities, ordered newest first.
        """
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id, frequency=frequency.value)
            .order_by("-created_at")
        )
        return [self._to_domain(h) for h in django_habits]

    def save(self, habit: DomainHabit) -> DomainHabit:
        """
        Save updates for an existing DomainHabit and return the stored DomainHabit.

        This attempts to load the corresponding DjangoHabit by habit.habit_id, applies fields from
        the provided DomainHabit, persists the model, and returns the resulting DomainHabit.
        The provided DomainHabit must reference an existing habit (habit.habit_id); this method
        does not create new records.

        Parameters:
            habit (DomainHabit): Domain entity containing updated values; its `habit_id` is used
                to locate the existing Django model.

        Returns:
            DomainHabit: The saved habit mapped back to the domain representation.

        Raises:
            ValueError: If the habit_id is invalid or no matching habit exists.
        """
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
        """
        Create a new Habit record in the database from a DomainHabit and return the saved domain entity.

        Parameters:
            habit (DomainHabit): Domain entity to persist. On success its habit_id is updated with the created model's ID.

        Returns:
            DomainHabit: Domain representation of the saved habit, including the assigned habit_id.
        """
        django_habit = self._from_domain(habit)
        django_habit.save()
        # Update habit_id with the generated ID
        habit.habit_id = str(django_habit.id)
        return self._to_domain(django_habit)

    def delete(self, habit_id: str) -> bool:
        """
        Delete a habit by its ID.

        Attempts to convert `habit_id` to an integer and delete the corresponding DjangoHabit.
        Returns True if a habit was found and deleted; returns False if the id is invalid or no habit exists for that id.
        """
        try:
            DjangoHabit.objects.get(id=int(habit_id)).delete()
            return True
        except (DjangoHabit.DoesNotExist, ValueError):
            return False

    def get_due_today(self, user_id: int) -> list[DomainHabit]:
        """
        Return the list of DomainHabit objects for habits considered "due" today for the given user.

        This uses a simplified rule based on the habit's `last_practiced` and `frequency`:
        - Never-practiced habits (last_practiced is null) are due.
        - Daily habits are due if not practiced yesterday.
        - Weekly habits are due if not practiced within the last 7 days.
        - Monthly habits are due if not practiced within the last 30 days.

        Parameters:
            user_id (int): ID of the user whose habits to evaluate.

        Returns:
            List[DomainHabit]: Domain representations of habits considered due today.
        """
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
    ) -> list[DomainHabit]:
        """
        Return the user's habits whose current streak is at least `min_streak`, ordered by streak length descending.

        Parameters:
            user_id (int): Primary key of the user whose habits to query.
            min_streak (int): Minimum current streak (inclusive) required for a habit to be returned. Defaults to 7.

        Returns:
            List[DomainHabit]: DomainHabit objects matching the filter, ordered by `current_streak` descending.
        """
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=user_id, current_streak__gte=min_streak)
            .order_by("-current_streak")
        )
        return [self._to_domain(h) for h in django_habits]

    def search_habits(
        self, user_id: int, query: str, limit: int = 20
    ) -> list[DomainHabit]:
        """
        Search a user's habits by name or description (case-insensitive) and return matching domain objects.

        Performs a case-insensitive match against habit name and description, returns results ordered by creation time (newest first) and limited to `limit` entries.

        Parameters:
            user_id (int): ID of the user whose habits to search.
            query (str): Substring to search for in habit name or description.
            limit (int): Maximum number of results to return (default 20).

        Returns:
            List[DomainHabit]: Matching habits converted to domain entities.
        """
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
        """
        Create a DjangoHabitCompletion model instance from a DomainHabitCompletion.

        The function looks up the related DjangoHabit using domain_completion.habit_id and builds
        an unsaved DjangoHabitCompletion populated with date, count, notes, and experience_gained
        from the domain object.

        Parameters:
            domain_completion (DomainHabitCompletion): Domain entity containing completion data;
                its habit_id must reference an existing DjangoHabit.

        Returns:
            DjangoHabitCompletion: Unsaved model instance ready to be saved().

        Raises:
            DjangoHabit.DoesNotExist: If no DjangoHabit exists for the given habit_id.
        """
        habit = DjangoHabit.objects.get(id=int(domain_completion.habit_id))

        return DjangoHabitCompletion(
            habit=habit,
            date=domain_completion.completion_date,
            count=domain_completion.count,
            notes=domain_completion.notes,
            experience_gained=domain_completion.experience_gained,
        )

    def create(self, completion: DomainHabitCompletion) -> DomainHabitCompletion:
        """
        Create and persist a new habit completion from a domain entity.

        Converts the provided DomainHabitCompletion into a Django model, saves it, updates
        the input object's `completion_id` with the generated database id, and returns
        the persisted DomainHabitCompletion reflecting the saved record.

        Parameters:
            completion (DomainHabitCompletion): Domain entity to create; its `completion_id` will be set after save.

        Returns:
            DomainHabitCompletion: The persisted domain object with `completion_id` populated.
        """
        django_completion = self._from_domain(completion)
        django_completion.save()
        # Update completion_id with the generated ID
        completion.completion_id = str(django_completion.id)
        return self._to_domain(django_completion)

    def get_by_habit_id(
        self, habit_id: str, limit: int = 100
    ) -> list[DomainHabitCompletion]:
        """
        Return completions for a habit ordered by date (newest first).

        Returns up to `limit` completions for the habit identified by `habit_id`.
        If `habit_id` is not a valid integer or no completions are found, an empty list is returned.

        Parameters:
            habit_id: Habit identifier as a string (must be convertible to int).
            limit: Maximum number of completions to return (default 100).

        Returns:
            List[DomainHabitCompletion]: Completions mapped to domain objects, ordered by descending date.
        """
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
    ) -> list[DomainHabitCompletion]:
        """
        Retrieve habit completion records for a specific user, ordered by completion date (newest first).

        Parameters:
            user_id (int): ID of the user whose habit completions to retrieve.
            limit (int): Maximum number of completions to return (default 100).

        Returns:
            List[DomainHabitCompletion]: Domain objects for the user's habit completions, ordered by date descending and limited by `limit`.
        """
        django_completions = (
            DjangoHabitCompletion.objects.select_related("habit__user")
            .filter(habit__user_id=user_id)
            .order_by("-date")[:limit]
        )
        return [self._to_domain(c) for c in django_completions]

    def get_by_date_range(
        self, habit_id: str, start_date: date, end_date: date
    ) -> list[DomainHabitCompletion]:
        """
        Return habit completions for a habit within an inclusive date range.

        start_date and end_date are inclusive; results are ordered by date ascending.
        If habit_id is not a valid integer or the habit does not exist, an empty list is returned.
        """
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
    ) -> DomainHabitCompletion | None:
        """
        Return the DomainHabitCompletion for a given habit and date, or None if not found.

        Parameters:
            habit_id (str): Habit primary key as a string (must be convertible to int).
            completion_date (date): Date of the completion to retrieve.

        Returns:
            Optional[DomainHabitCompletion]: Domain object for the completion, or None if the habit/completion does not exist or the habit_id is invalid.
        """
        try:
            django_completion = DjangoHabitCompletion.objects.select_related(
                "habit__user"
            ).get(habit_id=int(habit_id), date=completion_date)
            return self._to_domain(django_completion)
        except (DjangoHabitCompletion.DoesNotExist, ValueError):
            return None

    def delete_completion(self, completion_id: str) -> bool:
        """
        Delete a habit completion by its ID.

        Attempts to convert the given string ID to an integer and delete the corresponding
        DjangoHabitCompletion. Returns True when a record was found and deleted; returns
        False when the ID is invalid or no matching completion exists.

        Parameters:
            completion_id (str): The completion's numeric ID as a string (must be convertible to int).

        Returns:
            bool: True if deletion succeeded, False if the completion was not found or the ID was invalid.
        """
        try:
            DjangoHabitCompletion.objects.get(id=int(completion_id)).delete()
            return True
        except (DjangoHabitCompletion.DoesNotExist, ValueError):
            return False

    def get_streak_data(
        self, habit_id: str, days: int = 365
    ) -> list[DomainHabitCompletion]:
        """
        Return completions for a habit over a past window suitable for streak calculations.

        Retrieves completions for the habit with id `habit_id` from (today - `days`) up to today, inclusive.
        Delegates to `get_by_date_range` and returns a list of DomainHabitCompletion; on invalid `habit_id` an empty list is returned.

        Parameters:
            habit_id (str): UUID/string identifier of the habit.
            days (int): Number of days in the lookback window (default 365).

        Returns:
            List[DomainHabitCompletion]: Completions ordered by date within the requested range.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.get_by_date_range(habit_id, start_date, end_date)

    def get_completion_stats(self, user_id: int, days: int = 30) -> dict[str, Any]:
        """
        Return aggregate habit completion statistics for a user over a recent date window.

        Calculates totals for completions and experience gained between today - days and today (inclusive)
        and computes a simplified completion rate as:
            (total_completions) / (total_habits * days) * 100

        Parameters:
            user_id (int): ID of the user to compute statistics for.
            days (int): Number of days in the lookback window (default 30).

        Returns:
            Dict[str, Any]: A dictionary with keys:
                - total_completions (int): Count of habit completions in the window.
                - total_experience (int | None): Sum of experience_gained (None if no rows).
                - completion_rate (float): Percentage as described above (0.0 if user has no habits).
        """
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
