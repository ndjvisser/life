"""
Cross-context read-only query layer.

This module provides a thin abstraction for cross-context data access
without violating bounded context boundaries. Only read-only operations
are allowed to maintain context independence.
"""

from typing import Any

from django.contrib.auth import get_user_model


class CrossContextQueries:
    """
    Read-only queries that can safely access data across contexts.

    This class provides a controlled way to access data from multiple contexts
    without creating tight coupling. All methods are read-only and return
    simple data structures (dicts, lists) rather than domain objects.
    """

    @staticmethod
    def get_user_summary(user_id: int) -> dict[str, Any] | None:
        """
        Build a read-only summary of a user suitable for cross-context consumption.

        Returns a plain dict with basic user fields and, when available, additional grouped data
        from optional related objects. Always returns simple types (ints, strings, datetimes,
        nested dicts) and never domain model instances.

        Parameters:
            user_id (int): Primary key of the User to summarize.

        Returns:
            Optional[Dict[str, Any]]: Summary dict or None if no User with the given id exists.

        Summary contents:
            - Always present:
                - user_id, username, email, first_name, last_name, is_active, date_joined
            - If a related `profile` exists:
                - experience_points, level, bio, location
            - If a legacy `stats` relation exists:
                - legacy_level, legacy_experience
            - If a `core_stats` relation exists:
                - core_stats (dict) with keys: strength, endurance, agility, intelligence,
                  wisdom, charisma, level, experience_points
        """
        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)

            # Get basic user info
            summary = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }

            # Add profile info if available
            if hasattr(user, "profile"):
                summary.update(
                    {
                        "experience_points": user.profile.experience_points,
                        "level": user.profile.level,
                        "bio": user.profile.bio,
                        "location": user.profile.location,
                    }
                )

            # Add stats info if available (legacy support)
            if hasattr(user, "stats"):
                summary.update(
                    {
                        "legacy_level": user.stats.level,
                        "legacy_experience": user.stats.experience,
                    }
                )

            # Add core stats if available
            if hasattr(user, "core_stats"):
                summary.update(
                    {
                        "core_stats": {
                            "strength": user.core_stats.strength,
                            "endurance": user.core_stats.endurance,
                            "agility": user.core_stats.agility,
                            "intelligence": user.core_stats.intelligence,
                            "wisdom": user.core_stats.wisdom,
                            "charisma": user.core_stats.charisma,
                            "level": user.core_stats.level,
                            "experience_points": user.core_stats.experience_points,
                        }
                    }
                )

            return summary

        except get_user_model().DoesNotExist:
            return None

    @staticmethod
    def get_user_activity_counts(user_id: int) -> dict[str, int]:
        """
        Return counts of the user's activities across bounded contexts for dashboard use.

        Returns a dictionary with integer counts for the following keys:
        - "active_quests"
        - "completed_quests"
        - "active_habits"
        - "journal_entries"
        - "achievements"
        - "skills"

        If the user does not exist or a related context is not available on the user object, the corresponding counts remain zero.
        """
        counts = {
            "active_quests": 0,
            "completed_quests": 0,
            "active_habits": 0,
            "journal_entries": 0,
            "achievements": 0,
            "skills": 0,
        }

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)

            # Quest counts (use explicit related_name="quests")
            if hasattr(user, "quests"):
                counts["active_quests"] = user.quests.filter(status="active").count()
                counts["completed_quests"] = user.quests.filter(
                    status="completed"
                ).count()

            # Habit counts (use explicit related_name="habits")
            if hasattr(user, "habits"):
                counts["active_habits"] = user.habits.count()

            # Journal counts
            if hasattr(user, "journal_entries"):
                counts["journal_entries"] = user.journal_entries.count()

            # Achievement counts
            if hasattr(user, "achievements"):
                counts["achievements"] = user.achievements.count()

            # Skills counts
            if hasattr(user, "skills"):
                counts["skills"] = user.skills.count()

        except get_user_model().DoesNotExist:
            pass

        return counts

    @staticmethod
    def get_recent_activity(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        """
        Build a unified, read-only recent activity feed for a user across available contexts.

        Returns a list of activity items (newest first) composed from any available related data (quests, habit completions, journal entries, achievements). Each item is a plain dict with at least:
        - "type" (str): activity kind, e.g. "quest_completed", "habit_completed", "journal_entry", "achievement_unlocked"
        - "title" (str): human-facing title for the activity
        - "timestamp" (datetime): when the activity occurred
        - "context" (str): originating bounded context, e.g. "quests", "journals", "achievements"

        Context-specific additional keys may appear:
        - quests: "experience_reward" (int)
        - habits: "experience_gained" (int)
        - journal entries: "entry_type" (str)
        - achievements: "tier" (int or str)

        Parameters:
            user_id (int): primary key of the user to query.
            limit (int): maximum number of activity items to return (default 10).

        Returns:
            List[Dict[str, Any]]: up to `limit` activity dicts sorted by timestamp descending. Returns an empty list if the user does not exist or no related activity is available.
        """
        activities = []

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)

            # Recent quest completions (use explicit related_name="quests")
            if hasattr(user, "quests"):
                recent_quests = user.quests.filter(
                    status="completed", completed_at__isnull=False
                ).order_by("-completed_at")[:5]

                for quest in recent_quests:
                    activities.append(
                        {
                            "type": "quest_completed",
                            "title": quest.title,
                            "timestamp": quest.completed_at,
                            "experience_reward": quest.experience_reward,
                            "context": "quests",
                        }
                    )

            # Recent habit completions (use explicit related_name="habits")
            if hasattr(user, "habits"):
                from life_dashboard.quests.models import HabitCompletion

                recent_habits = HabitCompletion.objects.filter(
                    habit__user=user
                ).order_by("-date")[:5]

                for completion in recent_habits:
                    activity = {
                        "type": "habit_completed",
                        "title": completion.habit.name,
                        "timestamp": completion.date,
                        "context": "quests",
                    }

                    if hasattr(completion, "experience_gained"):
                        activity["experience_gained"] = completion.experience_gained

                    activities.append(activity)

            # Recent journal entries
            if hasattr(user, "journal_entries"):
                recent_entries = user.journal_entries.order_by("-created_at")[:5]

                for entry in recent_entries:
                    activities.append(
                        {
                            "type": "journal_entry",
                            "title": entry.title,
                            "timestamp": entry.created_at,
                            "entry_type": entry.entry_type,
                            "context": "journals",
                        }
                    )

            # Recent achievements
            if hasattr(user, "achievements"):
                recent_achievements = user.achievements.order_by("-unlocked_at")[:5]

                for achievement in recent_achievements:
                    activities.append(
                        {
                            "type": "achievement_unlocked",
                            "title": achievement.achievement.name,
                            "timestamp": achievement.unlocked_at,
                            "tier": achievement.achievement.tier,
                            "context": "achievements",
                        }
                    )

            # Sort by timestamp and limit
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:limit]

        except get_user_model().DoesNotExist:
            return []

    @staticmethod
    def get_context_health_check() -> dict[str, bool]:
        """
        Return a mapping of bounded context names to booleans indicating whether each context's models module is importable.

        Checks availability for the following contexts: "dashboard", "stats", "quests", "skills", "achievements", and "journals". Returns a dict where each key is the context name and the value is True when the corresponding `life_dashboard.<context>.models` module can be found, otherwise False.
        """
        health = {}

        import importlib.util

        # Check dashboard context
        health["dashboard"] = (
            importlib.util.find_spec("life_dashboard.dashboard.models") is not None
        )

        # Check stats context
        health["stats"] = (
            importlib.util.find_spec("life_dashboard.stats.models") is not None
        )

        # Check quests context
        health["quests"] = (
            importlib.util.find_spec("life_dashboard.quests.models") is not None
        )

        # Check skills context
        health["skills"] = (
            importlib.util.find_spec("life_dashboard.skills.models") is not None
        )

        # Check achievements context
        health["achievements"] = (
            importlib.util.find_spec("life_dashboard.achievements.models") is not None
        )

        # Check journals context
        health["journals"] = (
            importlib.util.find_spec("life_dashboard.journals.models") is not None
        )

        return health

    @staticmethod
    def get_user_preferences(user_id: int) -> dict[str, Any]:
        """
        Return a read-only, safe dictionary of user preferences suitable for cross-context sharing.

        Begins with sensible defaults:
        - timezone (str), date_format (str), experience_notifications (bool),
          achievement_notifications (bool), daily_summary (bool).

        If the User with the given primary key exists and has a related profile, the returned
        dict may also include:
        - location (str): profile.location, when present.
        - birth_date (date): profile.birth_date, when present.

        If no User with user_id exists, the function returns the default preferences unchanged.
        """
        preferences = {
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "experience_notifications": True,
            "achievement_notifications": True,
            "daily_summary": True,
        }

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)

            # Add any user-specific preferences from profile
            if hasattr(user, "profile"):
                # Add location-based timezone if available
                if user.profile.location:
                    preferences["location"] = user.profile.location

                # Add birth date for age-based features
                if user.profile.birth_date:
                    preferences["birth_date"] = user.profile.birth_date

        except get_user_model().DoesNotExist:
            pass

        return preferences


# Convenience functions for common cross-context queries
def get_user_dashboard_data(user_id: int) -> dict[str, Any]:
    """
    Assemble and return all read-only data required for a user's main dashboard.

    Returns a dictionary with these keys:
    - user_summary (Optional[Dict[str, Any]]): Comprehensive read-only summary of the user or None if the user doesn't exist.
    - activity_counts (Dict[str, int]): Counts of user activities (quests, habits, journal entries, achievements, skills).
    - recent_activity (List[Dict[str, Any]]): Unified recent activity feed across contexts, sorted most-recent-first (limited by the underlying query).
    - preferences (Dict[str, Any]): Safe, read-only user preferences with sensible defaults when unset.
    """
    return {
        "user_summary": CrossContextQueries.get_user_summary(user_id),
        "activity_counts": CrossContextQueries.get_user_activity_counts(user_id),
        "recent_activity": CrossContextQueries.get_recent_activity(user_id),
        "preferences": CrossContextQueries.get_user_preferences(user_id),
    }


def get_user_basic_info(user_id: int) -> dict[str, Any] | None:
    """
    Return a compact, read-only subset of a user's public information suitable for cross-context sharing.

    If the user does not exist the function returns None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary with the following keys when a user is found:
            - user_id (int): The user's identifier.
            - username (str): The user's username.
            - first_name (str): The user's first name (empty string if not available).
            - last_name (str): The user's last name (empty string if not available).
            - level (int): User level (defaults to 1 if missing).
            - experience_points (int): Experience points (defaults to 0 if missing).
    """
    summary = CrossContextQueries.get_user_summary(user_id)
    if not summary:
        return None

    # Return only the most basic, safe information
    return {
        "user_id": summary["user_id"],
        "username": summary["username"],
        "first_name": summary.get("first_name", ""),
        "last_name": summary.get("last_name", ""),
        "level": summary.get("level", 1),
        "experience_points": summary.get("experience_points", 0),
    }
