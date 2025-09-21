"""Quests infrastructure repositories - Django ORM implementations."""

from datetime import date, datetime, timedelta
from typing import Any

from django.contrib.auth.models import User
from django.db.models import Count, Max, Q

from ..domain.entities import Habit as DomainHabit
from ..domain.entities import HabitCompletion as DomainHabitCompletion
from ..domain.entities import HabitFrequency, QuestDifficulty, QuestStatus, QuestType
from ..domain.entities import Quest as DomainQuest
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
from ..models import Habit as DjangoHabit
from ..models import HabitCompletion as DjangoHabitCompletion
from ..models import Quest as DjangoQuest


def _quest_id_as_int(quest_id: QuestId | int | str | None) -> int:
    """Normalize quest identifiers to integers for ORM operations."""

    if isinstance(quest_id, QuestId):
        return quest_id.value
    if isinstance(quest_id, int):
        return quest_id
    if isinstance(quest_id, str):
        quest_id = quest_id.strip()
        if not quest_id:
            raise ValueError("Quest ID cannot be blank")
        return int(quest_id)
    raise ValueError(f"Invalid quest_id: {quest_id}")


def _habit_id_as_int(habit_id: HabitId | int | str | None) -> int:
    """Normalize habit identifiers to integers for ORM operations."""

    if isinstance(habit_id, HabitId):
        return habit_id.value
    if isinstance(habit_id, int):
        return habit_id
    if isinstance(habit_id, str):
        habit_id = habit_id.strip()
        if not habit_id:
            raise ValueError("Habit ID cannot be blank")
        return int(habit_id)
    raise ValueError(f"Invalid habit_id: {habit_id}")


def _completion_id_as_int(completion_id: str | int | None) -> int:
    """Normalize completion identifiers to integers for ORM operations."""

    if isinstance(completion_id, int):
        if completion_id <= 0:
            raise ValueError("Completion ID must be positive")
        return completion_id

    if completion_id is None:
        raise ValueError("Completion ID is required")

    text_value = str(completion_id).strip()
    if not text_value:
        raise ValueError("Completion ID cannot be blank")

    if not text_value.isdigit():
        raise ValueError(f"Invalid completion_id: {completion_id}")

    numeric_value = int(text_value)
    if numeric_value <= 0:
        raise ValueError("Completion ID must be positive")
    return numeric_value


def _user_id_as_int(user_id: UserId | int | str) -> int:
    """Normalize user identifiers to integers for ORM operations."""

    if isinstance(user_id, UserId):
        return user_id.value
    if isinstance(user_id, int):
        return user_id
    if isinstance(user_id, str):
        user_id = user_id.strip()
        if not user_id:
            raise ValueError("User ID cannot be blank")
        return int(user_id)
    raise ValueError(f"Invalid user_id: {user_id}")


def _value(raw: Any) -> Any:
    """Extract primitive values from value objects when persisting to the ORM."""

    return raw.value if hasattr(raw, "value") else raw


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
            user_id=UserId(django_quest.user.id),
            title=QuestTitle(django_quest.title),
            description=QuestDescription(django_quest.description or ""),
            difficulty=QuestDifficulty(django_quest.difficulty),
            quest_type=QuestType(django_quest.quest_type),
            status=QuestStatus(django_quest.status),
            experience_reward=ExperienceReward(django_quest.experience_reward),
            quest_id=QuestId(django_quest.id),
            progress=0.0,
            start_date=django_quest.start_date,
            due_date=django_quest.due_date,
            completed_at=django_quest.completed_at,
            parent_quest_id=(
                str(django_quest.parent_quest_id)
                if hasattr(django_quest, "parent_quest_id")
                and django_quest.parent_quest_id is not None
                else None
            ),
            prerequisite_quest_ids=[],
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
            user = User.objects.get(id=_user_id_as_int(domain_quest.user_id))
            django_quest = DjangoQuest(user=user)

        django_quest.title = _value(domain_quest.title)
        django_quest.description = _value(domain_quest.description)
        django_quest.quest_type = domain_quest.quest_type.value
        django_quest.difficulty = domain_quest.difficulty.value
        django_quest.status = domain_quest.status.value
        django_quest.experience_reward = _value(domain_quest.experience_reward)
        django_quest.start_date = domain_quest.start_date
        django_quest.due_date = domain_quest.due_date
        django_quest.completed_at = domain_quest.completed_at

        if domain_quest.updated_at:
            django_quest.updated_at = domain_quest.updated_at
        if hasattr(django_quest, "parent_quest_id"):
            if domain_quest.parent_quest_id is None:
                django_quest.parent_quest_id = None
            else:
                django_quest.parent_quest_id = _quest_id_as_int(
                    domain_quest.parent_quest_id
                )

        return django_quest

    def get_by_id(self, quest_id: QuestId | int | str) -> DomainQuest | None:
        """
        Retrieve a DomainQuest by its string ID.

        Converts the provided quest_id to an integer and returns the corresponding DomainQuest, or None if the ID is invalid or no matching DjangoQuest exists.
        """
        try:
            django_quest = DjangoQuest.objects.select_related("user").get(
                id=_quest_id_as_int(quest_id)
            )
            return self._to_domain(django_quest)
        except (DjangoQuest.DoesNotExist, ValueError):
            return None

    # ------------------------------------------------------------------
    # Compatibility aliases for legacy call sites expecting collection semantics
    # ------------------------------------------------------------------
    def find_by_id(self, quest_id: QuestId | int | str) -> DomainQuest | None:
        """Alias for :meth:`get_by_id` preserving QuestRepository API compatibility."""

        return self.get_by_id(quest_id)

    def list_for_user(self, user_id: UserId | int | str) -> list[DomainQuest]:
        """Alias for :meth:`get_by_user_id` to satisfy legacy repository naming."""

        return self.get_by_user_id(user_id)

    def list_by_status(
        self, user_id: UserId | int | str, status: QuestStatus
    ) -> list[DomainQuest]:
        """Alias for :meth:`get_by_status` preserving abstract repository contract."""

        return self.get_by_status(user_id, status)

    def list_by_type(
        self, user_id: UserId | int | str, quest_type: QuestType
    ) -> list[DomainQuest]:
        """Alias for :meth:`get_by_type` preserving abstract repository contract."""

        return self.get_by_type(user_id, quest_type)

    def get_by_user_id(self, user_id: UserId | int | str) -> list[DomainQuest]:
        """
        Return all quests belonging to the given user as DomainQuest objects.

        Results are ordered by creation time descending (newest first). Returns an empty list if the user has no quests.
        """
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=_user_id_as_int(user_id))
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_user_quests(self, user_id: UserId | int | str) -> list[DomainQuest]:
        """Return all quests for a user (alias of get_by_user_id for compatibility)."""

        return self.get_by_user_id(user_id)

    def get_active_quests(self, user_id: UserId | int | str) -> list[DomainQuest]:
        """Return quests currently in the ACTIVE status for the given user."""

        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=_user_id_as_int(user_id), status=QuestStatus.ACTIVE.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_status(
        self, user_id: UserId | int | str, status: QuestStatus
    ) -> list[DomainQuest]:
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
            .filter(user_id=_user_id_as_int(user_id), status=status.value)
            .order_by("-created_at")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_type(
        self, user_id: UserId | int | str, quest_type: QuestType
    ) -> list[DomainQuest]:
        """Get quests by type for a user."""
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(user_id=_user_id_as_int(user_id), quest_type=quest_type.value)
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
        if quest.quest_id is None:
            raise ValueError("Quest ID is required to save a quest")

        quest_identifier = _quest_id_as_int(quest.quest_id)

        try:
            django_quest = DjangoQuest.objects.select_related("user").get(
                id=quest_identifier
            )
            django_quest = self._from_domain(quest, django_quest)
            django_quest.save()
            return self._to_domain(django_quest)
        except (DjangoQuest.DoesNotExist, ValueError) as err:
            raise ValueError(f"Quest {quest_identifier} not found") from err

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
        quest.quest_id = QuestId(django_quest.id)
        return self._to_domain(django_quest)

    def delete(self, quest_id: QuestId | int | str) -> bool:
        """
        Delete a quest by its ID.

        Attempts to delete the DjangoQuest with the given string `quest_id` (expected to be an integer string).
        Returns True if the quest was found and deleted; returns False if the id is invalid or no matching quest exists.
        """
        try:
            DjangoQuest.objects.get(id=_quest_id_as_int(quest_id)).delete()
            return True
        except (DjangoQuest.DoesNotExist, ValueError):
            return False

    def get_overdue_quests(self, user_id: UserId | int | str) -> list[DomainQuest]:
        """
        Return the user's quests that are past their due date.

        Filters quests belonging to the given user with due_date < today and status in ("active", "paused"), ordered by due_date ascending. Returns a list of DomainQuest objects representing those overdue quests.
        """
        today = date.today()
        django_quests = (
            DjangoQuest.objects.select_related("user")
            .filter(
                user_id=_user_id_as_int(user_id),
                due_date__lt=today,
                status__in=["active", "paused"],
            )
            .order_by("due_date")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_due_soon(
        self, user_id: UserId | int | str, days: int = 7
    ) -> list[DomainQuest]:
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
                user_id=_user_id_as_int(user_id),
                due_date__gte=today,
                due_date__lte=future_date,
                status="active",
            )
            .order_by("due_date")
        )
        return [self._to_domain(q) for q in django_quests]

    def get_by_parent_quest(self, parent_quest_id: QuestId) -> list[DomainQuest]:
        """
        Return child DomainQuest objects for a given parent quest ID.

        Retrieves DjangoQuest rows with parent_quest_id equal to the provided ID, converts them to domain entities and returns them ordered by creation time (oldest first). If parent_quest_id cannot be coerced to an integer, an empty list is returned.

        Returns:
            List[DomainQuest]: Child quests ordered by created_at; empty list on invalid id or no children.
        """
        try:
            django_quests = (
                DjangoQuest.objects.select_related("user")
                .filter(parent_quest_id=_quest_id_as_int(parent_quest_id))
                .order_by("created_at")
            )
            return [self._to_domain(q) for q in django_quests]
        except ValueError:
            return []

    def search_quests(
        self, user_id: UserId | int | str, query: str, limit: int = 20
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
            .filter(user_id=_user_id_as_int(user_id))
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

        Parameters:
            django_habit (DjangoHabit): The Django model instance to convert.

        Returns:
            DomainHabit: The corresponding domain entity.
        """
        return DomainHabit(
            user_id=UserId(django_habit.user.id),
            name=HabitName(django_habit.name),
            description=django_habit.description,
            frequency=HabitFrequency(django_habit.frequency),
            target_count=CompletionCount(django_habit.target_count),
            current_streak=StreakCount(django_habit.current_streak),
            longest_streak=StreakCount(django_habit.longest_streak),
            experience_reward=ExperienceReward(django_habit.experience_reward),
            habit_id=HabitId(django_habit.id),
            created_at=django_habit.created_at,
            updated_at=django_habit.updated_at,
        )

    def _from_domain(
        self, domain_habit: DomainHabit, django_habit: DjangoHabit | None = None
    ) -> DjangoHabit:
        """
        Builds or updates a DjangoHabit model from a DomainHabit entity.

        If `django_habit` is not provided, the function fetches the User by `domain_habit.user_id`
        and constructs a new DjangoHabit instance attached to that user. Fields copied from the
        domain object include: name, description, frequency (uses the enum's `.value`), target_count,
        current_streak, longest_streak, and experience_reward.
        If `domain_habit.updated_at` is present, it is applied to the model.

        Returns:
            DjangoHabit: The created or updated Django model instance (not saved to the database).
        """
        if django_habit is None:
            user = User.objects.get(id=_user_id_as_int(domain_habit.user_id))
            django_habit = DjangoHabit(user=user)

        django_habit.name = _value(domain_habit.name)
        django_habit.description = domain_habit.description
        django_habit.frequency = domain_habit.frequency.value
        django_habit.target_count = _value(domain_habit.target_count)
        django_habit.current_streak = _value(domain_habit.current_streak)
        django_habit.longest_streak = _value(domain_habit.longest_streak)
        django_habit.experience_reward = _value(domain_habit.experience_reward)

        if domain_habit.updated_at:
            django_habit.updated_at = domain_habit.updated_at

        return django_habit

    def get_by_id(self, habit_id: HabitId | int | str) -> DomainHabit | None:
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
                id=_habit_id_as_int(habit_id)
            )
            return self._to_domain(django_habit)
        except (DjangoHabit.DoesNotExist, ValueError):
            return None

    def get_by_user_id(self, user_id: UserId | int | str) -> list[DomainHabit]:
        """Get all habits for a user."""
        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=_user_id_as_int(user_id))
            .order_by("-created_at")
        )
        return [self._to_domain(h) for h in django_habits]

    def get_user_habits(self, user_id: UserId | int | str) -> list[DomainHabit]:
        """Return all habits for a user (compatibility wrapper)."""

        return self.get_by_user_id(user_id)

    def get_by_frequency(
        self, user_id: UserId | int | str, frequency: HabitFrequency
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
            .filter(user_id=_user_id_as_int(user_id), frequency=frequency.value)
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
        if habit.habit_id is None:
            raise ValueError("Habit ID is required to save a habit")

        habit_identifier = _habit_id_as_int(habit.habit_id)

        try:
            django_habit = DjangoHabit.objects.select_related("user").get(
                id=habit_identifier
            )
            django_habit = self._from_domain(habit, django_habit)
            django_habit.save()
            return self._to_domain(django_habit)
        except (DjangoHabit.DoesNotExist, ValueError) as err:
            raise ValueError(f"Habit {habit_identifier} not found") from err

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
        habit.habit_id = HabitId(django_habit.id)
        return self._to_domain(django_habit)

    def delete(self, habit_id: HabitId | int | str) -> bool:
        """
        Delete a habit by its ID.

        Attempts to convert `habit_id` to an integer and delete the corresponding DjangoHabit.
        Returns True if a habit was found and deleted; returns False if the id is invalid or no habit exists for that id.
        """
        try:
            DjangoHabit.objects.get(id=_habit_id_as_int(habit_id)).delete()
            return True
        except (DjangoHabit.DoesNotExist, ValueError):
            return False

    def get_due_today(self, user_id: UserId | int | str) -> list[DomainHabit]:
        """
        Return the list of DomainHabit objects for habits considered "due" today for the given user.

        A habit is considered due when, based on its completion history, it has not
        been completed within the expected cadence for its frequency:

        - Habits with no completions are due.
        - Daily habits are due if they were not completed yesterday.
        - Weekly habits are due if they have not been completed in the last 7 days.
        - Monthly habits are due if they have not been completed in the last 30 days.

        Parameters:
            user_id (int): ID of the user whose habits to evaluate.

        Returns:
            List[DomainHabit]: Domain representations of habits considered due today.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        django_habits = (
            DjangoHabit.objects.select_related("user")
            .filter(user_id=_user_id_as_int(user_id))
            .annotate(last_completion_date=Max("completions__date"))
            .filter(
                Q(last_completion_date__isnull=True)
                | Q(
                    frequency="daily",
                    last_completion_date__lt=yesterday,
                )
                | Q(
                    frequency="weekly",
                    last_completion_date__lt=today - timedelta(days=7),
                )
                | Q(
                    frequency="monthly",
                    last_completion_date__lt=today - timedelta(days=30),
                )
            )
        )
        return [self._to_domain(h) for h in django_habits]

    def get_active_streaks(
        self, user_id: UserId | int | str, min_streak: int = 7
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
            .filter(user_id=_user_id_as_int(user_id), current_streak__gte=min_streak)
            .order_by("-current_streak")
        )
        return [self._to_domain(h) for h in django_habits]

    def search_habits(
        self, user_id: UserId | int | str, query: str, limit: int = 20
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
            .filter(user_id=_user_id_as_int(user_id))
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
        created_at_value = getattr(django_completion, "created_at", None)
        if created_at_value is None:
            created_at_value = datetime.combine(
                django_completion.date, datetime.min.time()
            )

        current_streak = django_completion.habit.current_streak

        return DomainHabitCompletion(
            completion_id=str(django_completion.id),
            habit_id=HabitId(django_completion.habit.id),
            user_id=UserId(django_completion.habit.user.id),
            completion_date=django_completion.date,
            count=CompletionCount(django_completion.count),
            notes=django_completion.notes,
            experience_gained=ExperienceReward(
                django_completion.experience_gained
            ),
            streak_at_completion=StreakCount(current_streak or 0),
            created_at=created_at_value,
        )

    def _from_domain(
        self,
        domain_completion: DomainHabitCompletion,
        django_completion: DjangoHabitCompletion | None = None,
    ) -> DjangoHabitCompletion:
        """Create or update a DjangoHabitCompletion model from a domain entity.

        The function looks up the related DjangoHabit using ``domain_completion.habit_id`` and
        applies the domain data to ``django_completion``. When ``django_completion`` is omitted a
        new instance is constructed; otherwise the existing instance is updated in-place.

        Parameters:
            domain_completion (DomainHabitCompletion): Domain entity containing completion data;
                its habit_id must reference an existing DjangoHabit.

        Returns:
            DjangoHabitCompletion: Model instance populated with domain values (not yet saved).

        Raises:
            DjangoHabit.DoesNotExist: If no DjangoHabit exists for the given habit_id.
        """
        habit = DjangoHabit.objects.get(id=_habit_id_as_int(domain_completion.habit_id))

        if django_completion is None:
            django_completion = DjangoHabitCompletion(habit=habit)
        else:
            django_completion.habit = habit

        django_completion.date = domain_completion.completion_date
        django_completion.count = _value(domain_completion.count)
        django_completion.notes = domain_completion.notes or ""
        django_completion.experience_gained = _value(
            domain_completion.experience_gained
        )

        return django_completion

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

    def save(self, completion: DomainHabitCompletion) -> DomainHabitCompletion:
        """Persist changes to an existing completion or create a new one when needed."""

        if not completion.completion_id:
            return self.create(completion)

        try:
            completion_identifier = _completion_id_as_int(completion.completion_id)
        except ValueError as exc:
            raise ValueError("Invalid completion ID provided") from exc

        try:
            django_completion = DjangoHabitCompletion.objects.select_related(
                "habit__user"
            ).get(id=completion_identifier)
        except DjangoHabitCompletion.DoesNotExist as exc:
            raise ValueError(
                f"Habit completion {completion_identifier} not found"
            ) from exc

        django_completion = self._from_domain(completion, django_completion)
        django_completion.save()

        return self._to_domain(django_completion)

    def get_habit_completions(
        self,
        habit_id: HabitId | int | str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DomainHabitCompletion]:
        """Return completions for a habit, optionally filtered by an inclusive date range."""

        habit_identifier = _habit_id_as_int(habit_id)

        queryset = DjangoHabitCompletion.objects.select_related("habit__user").filter(
            habit_id=habit_identifier
        )

        if start_date is not None:
            queryset = queryset.filter(date__gte=start_date)
        if end_date is not None:
            queryset = queryset.filter(date__lte=end_date)

        queryset = queryset.order_by("-date", "-id")

        return [self._to_domain(completion) for completion in queryset]

    def get_completion_count(
        self, habit_id: HabitId, target_date: date
    ) -> int:
        """Return the number of completions recorded for a habit on a specific date."""

        habit_identifier = _habit_id_as_int(habit_id)

        return int(
            DjangoHabitCompletion.objects.filter(
                habit_id=habit_identifier, date=target_date
            ).count()
        )

    def get_latest_completion(
        self, habit_id: HabitId
    ) -> DomainHabitCompletion | None:
        """Return the most recent completion for the given habit."""

        habit_identifier = _habit_id_as_int(habit_id)

        django_completion = (
            DjangoHabitCompletion.objects.select_related("habit__user")
            .filter(habit_id=habit_identifier)
            .order_by("-date", "-id")
            .first()
        )

        return self._to_domain(django_completion) if django_completion else None

    def get_by_habit_id(
        self, habit_id: HabitId | int | str, limit: int | None = 100
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
            queryset = (
                DjangoHabitCompletion.objects.select_related("habit__user")
                .filter(habit_id=_habit_id_as_int(habit_id))
                .order_by("-date")
            )
            if limit is not None:
                queryset = queryset[:limit]
            django_completions = list(queryset)
            return [self._to_domain(c) for c in django_completions]
        except ValueError:
            return []

    def get_by_user_id(
        self, user_id: UserId | int | str, limit: int = 100
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
            .filter(habit__user_id=_user_id_as_int(user_id))
            .order_by("-date")[:limit]
        )
        return [self._to_domain(c) for c in django_completions]

    def get_by_date_range(
        self, habit_id: HabitId | int | str, start_date: date, end_date: date
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
                    habit_id=_habit_id_as_int(habit_id),
                    date__gte=start_date,
                    date__lte=end_date,
                )
                .order_by("date")
            )
            return [self._to_domain(c) for c in django_completions]
        except ValueError:
            return []

    def get_completion_for_date(
        self, habit_id: HabitId | int | str, completion_date: date
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
            ).get(habit_id=_habit_id_as_int(habit_id), date=completion_date)
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

    def get_completion_stats(
        self, user_id: UserId | int | str, days: int = 30
    ) -> dict[str, Any]:
        """
        Return aggregate habit completion statistics for a user over a recent date window.

        Calculates completion statistics including daily averages and streak information.

        Parameters:
            user_id (int): ID of the user to compute statistics for.
            days (int): Number of days in the lookback window (default 30).

        Returns:
            Dict[str, Any]: A dictionary with keys:
                - daily_average (float): Average completions per day over the period.
                - current_streak (int): Longest current streak across all habits.
                - longest_streak (int): Longest recorded streak across all habits.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get completion counts and experience
        user_identifier = _user_id_as_int(user_id)

        completions = DjangoHabitCompletion.objects.filter(
            habit__user_id=user_identifier, date__gte=start_date, date__lte=end_date
        )

        stats = completions.aggregate(
            total_completions=Count("id"),
        )

        # Get streak information from habits
        habits = DjangoHabit.objects.filter(user_id=user_identifier)
        current_streaks = [h.current_streak for h in habits if h.current_streak > 0]
        longest_streaks = [h.longest_streak for h in habits if h.longest_streak > 0]

        # Calculate daily average (completions per day)
        daily_avg = stats["total_completions"] / days if days > 0 else 0.0

        return {
            "daily_average": round(daily_avg, 2),
            "current_streak": max(current_streaks, default=0),
            "longest_streak": max(longest_streaks, default=0),
        }
