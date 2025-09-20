"""
Cross-context read-only query layer.

This module provides a thin abstraction for cross-context data access
without violating bounded context boundaries. Only read-only operations
are allowed to maintain context independence.
"""

from typing import Any, Dict, List, Optional

from django.contrib.auth.models import User


class CrossContextQueries:
    """
    Read-only queries that can safely access data across contexts.

    This class provides a controlled way to access data from multiple contexts
    without creating tight coupling. All methods are read-only and return
    simple data structures (dicts, lists) rather than domain objects.
    """

    @staticmethod
    def get_user_summary(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary of user data across all contexts.

        Returns basic information that can be safely shared between contexts.
        """
        try:
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

        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_activity_counts(user_id: int) -> Dict[str, int]:
        """
        Get activity counts across contexts for dashboard display.

        Returns counts of various user activities without exposing
        internal domain logic.
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
            user = User.objects.get(id=user_id)

            # Quest counts
            if hasattr(user, "quest_set"):
                counts["active_quests"] = user.quest_set.filter(status="active").count()
                counts["completed_quests"] = user.quest_set.filter(
                    status="completed"
                ).count()

            # Habit counts
            if hasattr(user, "habit_set"):
                counts["active_habits"] = user.habit_set.count()

            # Journal counts
            if hasattr(user, "journal_entries"):
                counts["journal_entries"] = user.journal_entries.count()

            # Achievement counts
            if hasattr(user, "achievements"):
                counts["achievements"] = user.achievements.count()

            # Skills counts
            if hasattr(user, "skills"):
                counts["skills"] = user.skills.count()

        except User.DoesNotExist:
            pass

        return counts

    @staticmethod
    def get_recent_activity(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activity across all contexts for activity feed.

        Returns a unified activity feed without exposing domain internals.
        """
        activities = []

        try:
            user = User.objects.get(id=user_id)

            # Recent quest completions
            if hasattr(user, "quest_set"):
                recent_quests = user.quest_set.filter(
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

            # Recent habit completions
            if hasattr(user, "habit_set"):
                from life_dashboard.quests.models import HabitCompletion

                recent_habits = HabitCompletion.objects.filter(
                    habit__user=user
                ).order_by("-date")[:5]

                for completion in recent_habits:
                    activities.append(
                        {
                            "type": "habit_completed",
                            "title": completion.habit.name,
                            "timestamp": completion.date,
                            "experience_gained": completion.experience_gained,
                            "context": "quests",
                        }
                    )

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

        except User.DoesNotExist:
            return []

    @staticmethod
    def get_context_health_check() -> Dict[str, bool]:
        """
        Check if all contexts are properly configured and accessible.

        Returns status of each bounded context for monitoring.
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
    def get_user_preferences(user_id: int) -> Dict[str, Any]:
        """
        Get user preferences that might be needed across contexts.

        Returns safe, read-only preference data.
        """
        preferences = {
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "experience_notifications": True,
            "achievement_notifications": True,
            "daily_summary": True,
        }

        try:
            user = User.objects.get(id=user_id)

            # Add any user-specific preferences from profile
            if hasattr(user, "profile"):
                # Add location-based timezone if available
                if user.profile.location:
                    preferences["location"] = user.profile.location

                # Add birth date for age-based features
                if user.profile.birth_date:
                    preferences["birth_date"] = user.profile.birth_date

        except User.DoesNotExist:
            pass

        return preferences


# Convenience functions for common cross-context queries
def get_user_dashboard_data(user_id: int) -> Dict[str, Any]:
    """Get all data needed for the main dashboard."""
    return {
        "user_summary": CrossContextQueries.get_user_summary(user_id),
        "activity_counts": CrossContextQueries.get_user_activity_counts(user_id),
        "recent_activity": CrossContextQueries.get_recent_activity(user_id),
        "preferences": CrossContextQueries.get_user_preferences(user_id),
    }


def get_user_basic_info(user_id: int) -> Optional[Dict[str, Any]]:
    """Get basic user info that's safe to share between contexts."""
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
