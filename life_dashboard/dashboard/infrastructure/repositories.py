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
        """
        Create a new Django User and return the new user's ID.

        The user is created inside an atomic transaction to ensure the operation is rolled back on error.

        Returns:
            int: ID of the newly created user.
        """
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
        """
        Return a dictionary of public user fields for the given user ID, or None if the user does not exist.

        Parameters:
            user_id (int): Primary key of the user to retrieve.

        Returns:
            Optional[dict]: Dictionary with keys 'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', and 'date_joined' when found; otherwise None.
        """
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
        """
        Retrieve a user's public fields by username.

        Returns a dictionary with keys `id`, `username`, `email`, `first_name`, `last_name`, `is_active`, and `date_joined` if a user with the given username exists; otherwise returns None.
        """
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
        """
        Update mutable fields on a Django User and persist the changes.

        Attempts to set each provided keyword argument on the User with the given id; only attributes that exist on the User instance are applied. Saves the User if found and returns True. Returns False if no User with the given id exists.

        Parameters:
            user_id (int): ID of the User to update.
            **kwargs: Field names and values to set on the User; unknown fields are ignored.

        Returns:
            bool: True if the user was found and saved; False if the user does not exist.
        """
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
        """
        Authenticate the given username and password and return the user's ID.

        Returns:
            Optional[int]: The authenticated user's primary key if credentials are valid; otherwise None.
        """
        user = authenticate(username=username, password=password)
        return user.id if user else None


class DjangoUserProfileRepository(UserProfileRepository):
    """Django ORM implementation of UserProfileRepository."""

    def _to_domain(self, django_profile: DjangoUserProfile) -> DomainUserProfile:
        """
        Convert a DjangoUserProfile model (including its related User) into a DomainUserProfile.

        The returned DomainUserProfile contains the user's id, username, first/last name, and email
        from the related User, plus profile fields: bio, location, birth_date, experience_points,
        level, created_at, and updated_at.

        Parameters:
            django_profile (DjangoUserProfile): Django model instance; its related `user` must be available.

        Returns:
            DomainUserProfile: Domain representation constructed from the Django model.
        """
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
        """
        Create or update a DjangoUserProfile from a DomainUserProfile.

        If `django_profile` is provided, its fields are updated from `domain_profile`.
        If `django_profile` is None, a new DjangoUserProfile is constructed and linked
        to the User referenced by `domain_profile.user_id`.

        Parameters:
            domain_profile (DomainUserProfile): Domain object containing profile data to copy.
            django_profile (Optional[DjangoUserProfile]): Existing Django model instance to update;
                if omitted, a new instance is created (not saved).

        Returns:
            DjangoUserProfile: The Django model instance populated with values from `domain_profile`.
            The returned instance is not saved to the database.

        Raises:
            django.contrib.auth.models.User.DoesNotExist: If creating a new profile and the
                referenced User (domain_profile.user_id) does not exist.
        """
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
        """
        Return the domain user profile for the given user ID, or None if not found.

        Retrieves the profile for the user identified by `user_id` and converts it to a
        DomainUserProfile. If no profile exists for that user, returns None.

        Parameters:
            user_id (int): Primary key of the Django User whose profile to retrieve.

        Returns:
            Optional[DomainUserProfile]: Domain representation of the user's profile, or None if missing.
        """
        try:
            django_profile = DjangoUserProfile.objects.select_related("user").get(
                user_id=user_id
            )
            return self._to_domain(django_profile)
        except DjangoUserProfile.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[DomainUserProfile]:
        """
        Return the DomainUserProfile for the given username.

        Retrieves the DjangoUserProfile joined with its related User by username and converts it to a DomainUserProfile via _to_domain.
        Returns None if no profile exists for the provided username.

        Parameters:
            username (str): The User.username to look up.

        Returns:
            Optional[DomainUserProfile]: The domain representation of the user's profile, or None if not found.
        """
        try:
            django_profile = DjangoUserProfile.objects.select_related("user").get(
                user__username=username
            )
            return self._to_domain(django_profile)
        except DjangoUserProfile.DoesNotExist:
            return None

    def save(self, profile: DomainUserProfile) -> DomainUserProfile:
        """
        Save updates to an existing user profile and return the updated DomainUserProfile.

        Fetches the DjangoUserProfile for profile.user_id, applies domain-to-model changes, persists them, and converts the saved model back to a DomainUserProfile.

        Parameters:
            profile (DomainUserProfile): Domain representation containing updated profile fields; must include user_id.

        Returns:
            DomainUserProfile: The saved profile reflecting persisted changes.

        Raises:
            ValueError: If no DjangoUserProfile exists for profile.user_id.
        """
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
        """
        Create and persist a new user profile from a DomainUserProfile.

        The provided domain profile is converted to a DjangoUserProfile, saved to the database,
        and the persisted profile is returned as a DomainUserProfile.

        Parameters:
            profile (DomainUserProfile): Domain representation of the profile to create.

        Returns:
            DomainUserProfile: The newly created profile with fields populated from the saved record.
        """
        django_profile = self._from_domain(profile)
        django_profile.save()
        return self._to_domain(django_profile)

    def exists_by_user_id(self, user_id: int) -> bool:
        """
        Return True if a user profile exists for the given user ID.

        Parameters:
            user_id (int): Primary key of the User to check.

        Returns:
            bool: True if a DjangoUserProfile exists for the user, otherwise False.
        """
        return DjangoUserProfile.objects.filter(user_id=user_id).exists()
