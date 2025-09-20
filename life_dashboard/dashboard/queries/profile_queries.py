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
        """
        Return a dictionary with a dashboard-ready summary for the given user's profile or None if no profile exists.
        
        The returned dict contains selected user fields, profile attributes and derived metrics:
        - user_id, username, full_name, first_name, last_name, email
        - bio, location, birth_date
        - experience_points, level
        - experience_to_next_level: non-negative points remaining to reach next level
        - level_progress_percentage: 0.0–100.0 float progress toward the next level
        - created_at, updated_at
        
        Returns:
            Optional[dict]: Profile summary dictionary or None when the UserProfile is not found.
        """
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
        """
        Return a dictionary of basic public fields for the given user or None if the user does not exist.
        
        The returned mapping contains:
        - id, username, email
        - first_name, last_name, full_name (first + last, trimmed)
        - is_active, date_joined
        
        Returns:
            Optional[Dict[str, Any]]: User info dict or None when no User with the given id exists.
        """
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
        """
        Return a QuerySet of top UserProfile records ordered by descending experience points.
        
        Parameters:
            limit (int): Maximum number of profiles to return (default 10).
        
        Returns:
            QuerySet: Slice of UserProfile objects (select_related('user')) ordered by `-experience_points`.
        """
        return UserProfile.objects.select_related("user").order_by(
            "-experience_points"
        )[:limit]

    @staticmethod
    def get_level_leaderboard(limit: int = 10) -> QuerySet:
        """
        Return the top user profiles ordered by level (ties broken by experience points).
        
        Returns a QuerySet of UserProfile objects (select_related("user")) ordered by descending
        level and then descending experience_points, limited to `limit` results.
        
        Parameters:
            limit (int): Maximum number of profiles to return (default 10).
        
        Returns:
            QuerySet: QuerySet of UserProfile records with related User prefetched.
        """
        return UserProfile.objects.select_related("user").order_by(
            "-level", "-experience_points"
        )[:limit]

    @staticmethod
    def search_profiles(query: str, limit: int = 20) -> QuerySet:
        """
        Return profiles whose username contains the given query (case-insensitive).
        
        Performs a case-insensitive substring match against the related User.username, orders results by username, and limits the returned queryset to `limit`. The queryset uses select_related("user") so each UserProfile contains its related User without additional queries.
        
        Parameters:
            query (str): Substring to search for within usernames (case-insensitive).
            limit (int): Maximum number of profiles to return (default: 20).
        
        Returns:
            QuerySet: A queryset of UserProfile instances (with related User selected), ordered by user.username and truncated to `limit`.
        """
        return (
            UserProfile.objects.select_related("user")
            .filter(user__username__icontains=query)
            .order_by("user__username")[:limit]
        )

    @staticmethod
    def _calculate_level_progress(profile: UserProfile) -> float:
        """
        Return the percentage progress of a profile's experience toward the next level.
        
        Calculates progress based on thresholds where each level spans 1000 experience points
        (i.e., level N ranges from (N-1)*1000 to N*1000). Results are clamped to a maximum of 100.0.
        If the computed level range is zero, the function returns 100.0.
        
        Parameters:
            profile (UserProfile): Profile instance; uses `profile.level` and `profile.experience_points`.
        
        Returns:
            float: Progress percentage in the range [0.0, 100.0].
        """
        current_level_threshold = (profile.level - 1) * 1000
        next_level_threshold = profile.level * 1000
        level_experience = profile.experience_points - current_level_threshold
        level_range = next_level_threshold - current_level_threshold

        if level_range == 0:
            return 100.0

        return min(100.0, (level_experience / level_range) * 100)
