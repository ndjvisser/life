"""
Dashboard profile queries - read-only data access for views.
"""

from typing import Any, Dict, Optional

from django.contrib.auth.models import User
from django.db.models import QuerySet

from ..models import UserProfile


class ProfileQueries:
    """Read-only queries for user profile data."""

    @staticmethod
    def get_profile_summary(user_id: int) -> Optional[Dict[str, Any]]:
        """Get profile summary for dashboard display."""
        try:
            profile = UserProfile.objects.select_related("user").get(user_id=user_id)
            return {
                "user_id": profile.user.id,
                "username": profile.user.username,
                "full_name": f"{profile.user.first_name} {profile.user.last_name}".strip(),
                "first_name": profile.user.first_name,
                "last_name": profile.user.last_name,
                "email": profile.user.email,
                "bio": profile.bio,
                "location": profile.location,
                "birth_date": profile.birth_date,
                "experience_points": profile.experience_points,
                "level": profile.level,
                "experience_to_next_level": max(
                    0, (profile.level * 1000) - profile.experience_points
                ),
                "level_progress_percentage": ProfileQueries._calculate_level_progress(
                    profile
                ),
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }
        except UserProfile.DoesNotExist:
            return None

    @staticmethod
    def get_user_basic_info(user_id: int) -> Optional[Dict[str, Any]]:
        """Get basic user information."""
        try:
            user = User.objects.get(id=user_id)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_experience_leaderboard(limit: int = 10) -> QuerySet:
        """Get top users by experience points."""
        return UserProfile.objects.select_related("user").order_by(
            "-experience_points"
        )[:limit]

    @staticmethod
    def get_level_leaderboard(limit: int = 10) -> QuerySet:
        """Get top users by level."""
        return UserProfile.objects.select_related("user").order_by(
            "-level", "-experience_points"
        )[:limit]

    @staticmethod
    def search_profiles(query: str, limit: int = 20) -> QuerySet:
        """Search user profiles by username or name."""
        return (
            UserProfile.objects.select_related("user")
            .filter(user__username__icontains=query)
            .order_by("user__username")[:limit]
        )

    @staticmethod
    def _calculate_level_progress(profile: UserProfile) -> float:
        """Calculate progress percentage towards next level."""
        current_level_threshold = (profile.level - 1) * 1000
        next_level_threshold = profile.level * 1000
        level_experience = profile.experience_points - current_level_threshold
        level_range = next_level_threshold - current_level_threshold

        if level_range == 0:
            return 100.0

        return min(100.0, (level_experience / level_range) * 100)
