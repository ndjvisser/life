"""
Dashboard infrastructure repositories - Django ORM implementations.
"""
from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction

from ..domain.entities import UserProfile as DomainUserProfile
from ..domain.repositories import UserProfileRepository, UserRepository
from ..models import UserProfile as DjangoUserProfile


class DjangoUserRepository(UserRepository):
    """Django ORM implementation of UserRepository."""

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> int:
        """Create new user and return user ID."""
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            return user.id

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user data by ID."""
        try:
            user = User.objects.get(id=user_id)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
        except User.DoesNotExist:
            return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user data by username."""
        try:
            user = User.objects.get(username=username)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            }
        except User.DoesNotExist:
            return None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields."""
        try:
            user = User.objects.get(id=user_id)
            for field, value in kwargs.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.save()
            return True
        except User.DoesNotExist:
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user ID if successful."""
        user = authenticate(username=username, password=password)
        return user.id if user else None


class DjangoUserProfileRepository(UserProfileRepository):
    """Django ORM implementation of UserProfileRepository."""

    def _to_domain(self, django_profile: DjangoUserProfile) -> DomainUserProfile:
        """Convert Django model to domain entity."""
        return DomainUserProfile(
            user_id=django_profile.user.id,
            username=django_profile.user.username,
            first_name=django_profile.user.first_name,
            last_name=django_profile.user.last_name,
            email=django_profile.user.email,
            bio=django_profile.bio,
            location=django_profile.location,
            birth_date=django_profile.birth_date,
            experience_points=django_profile.experience_points,
            level=django_profile.level,
            created_at=django_profile.created_at,
            updated_at=django_profile.updated_at,
        )

    def _from_domain(
        self,
        domain_profile: DomainUserProfile,
        django_profile: Optional[DjangoUserProfile] = None,
    ) -> DjangoUserProfile:
        """Convert domain entity to Django model."""
        if django_profile is None:
            # Create new Django profile
            user = User.objects.get(id=domain_profile.user_id)
            django_profile = DjangoUserProfile(user=user)

        # Update fields
        django_profile.bio = domain_profile.bio
        django_profile.location = domain_profile.location
        django_profile.birth_date = domain_profile.birth_date
        django_profile.experience_points = domain_profile.experience_points
        django_profile.level = domain_profile.level

        if domain_profile.updated_at:
            django_profile.updated_at = domain_profile.updated_at

        return django_profile

    def get_by_user_id(self, user_id: int) -> Optional[DomainUserProfile]:
        """Get user profile by user ID."""
        try:
            django_profile = DjangoUserProfile.objects.select_related("user").get(
                user_id=user_id
            )
            return self._to_domain(django_profile)
        except DjangoUserProfile.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[DomainUserProfile]:
        """Get user profile by username."""
        try:
            django_profile = DjangoUserProfile.objects.select_related("user").get(
                user__username=username
            )
            return self._to_domain(django_profile)
        except DjangoUserProfile.DoesNotExist:
            return None

    def save(self, profile: DomainUserProfile) -> DomainUserProfile:
        """Save user profile and return updated entity."""
        try:
            django_profile = DjangoUserProfile.objects.select_related("user").get(
                user_id=profile.user_id
            )
            django_profile = self._from_domain(profile, django_profile)
            django_profile.save()
            return self._to_domain(django_profile)
        except DjangoUserProfile.DoesNotExist as err:
            raise ValueError(
                f"User profile not found for user_id: {profile.user_id}"
            ) from err

    def create(self, profile: DomainUserProfile) -> DomainUserProfile:
        """Create new user profile."""
        django_profile = self._from_domain(profile)
        django_profile.save()
        return self._to_domain(django_profile)

    def exists_by_user_id(self, user_id: int) -> bool:
        """Check if profile exists for user ID."""
        return DjangoUserProfile.objects.filter(user_id=user_id).exists()
