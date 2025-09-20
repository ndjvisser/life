"""
Tests for atomic user creation functionality.
"""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from life_dashboard.dashboard.application.services import UserService
from life_dashboard.dashboard.infrastructure.repositories import (
    DjangoUserProfileRepository,
    DjangoUserRepository,
)
from life_dashboard.dashboard.models import UserProfile


@pytest.mark.django_db
class TestAtomicUserCreation:
    """Test cases for atomic user and profile creation."""

    def setup_method(self):
        """Set up test dependencies."""
        self.user_repo = DjangoUserRepository()
        self.profile_repo = DjangoUserProfileRepository()
        self.user_service = UserService(self.user_repo, self.profile_repo)

    def test_successful_atomic_creation(self):
        """Test that user and profile are created atomically on success."""
        # Arrange
        username = "atomictest"
        email = "atomic@test.com"

        # Act
        user_id, profile = self.user_service.register_user(
            username=username,
            email=email,
            password="testpass123",
            first_name="Atomic",
            last_name="Test",
            bio="Test bio",
            location="Test location",
        )

        # Assert
        assert user_id is not None
        assert profile is not None
        assert profile.username == username
        assert profile.first_name == "Atomic"
        assert profile.bio == "Test bio"
        assert profile.location == "Test location"

        # Verify both records exist in database
        assert User.objects.filter(id=user_id).exists()
        assert UserProfile.objects.filter(user_id=user_id).exists()

    def test_rollback_on_profile_failure(self):
        """Test that user creation is rolled back when profile update fails."""
        # Arrange
        initial_user_count = User.objects.count()
        initial_profile_count = UserProfile.objects.count()

        # Act & Assert
        with patch.object(
            UserProfile, "save", side_effect=Exception("Profile save failed")
        ):
            with pytest.raises(Exception, match="Profile save failed"):
                self.user_service.register_user(
                    username="failtest", email="fail@test.com", password="testpass123"
                )

        # Verify no records were created
        assert User.objects.count() == initial_user_count
        assert UserProfile.objects.count() == initial_profile_count

    def test_duplicate_username_handling(self):
        """Test that duplicate username attempts are handled correctly."""
        # Arrange - create first user
        self.user_service.register_user(
            username="duplicate", email="first@test.com", password="testpass123"
        )

        # Act & Assert - try to create duplicate
        with pytest.raises(IntegrityError):
            self.user_service.register_user(
                username="duplicate",  # Same username
                email="second@test.com",
                password="testpass123",
            )

        # Verify only one user exists
        assert User.objects.filter(username="duplicate").count() == 1

    def test_backward_compatibility(self):
        """Test that existing code calling register_user still works."""
        # Act - call with minimal parameters (old style)
        user_id, profile = self.user_service.register_user(
            username="backward", email="backward@test.com", password="testpass123"
        )

        # Assert - defaults are applied correctly
        assert profile.bio == ""
        assert profile.location == ""
        assert profile.username == "backward"

    def test_repository_atomic_method(self):
        """Test the repository's atomic method directly."""
        # Act
        user_id, profile = self.user_repo.create_user_with_profile(
            username="repotest",
            email="repo@test.com",
            password="testpass123",
            first_name="Repo",
            last_name="Test",
            bio="Repo bio",
            location="Repo location",
        )

        # Assert
        assert user_id is not None
        assert profile.username == "repotest"
        assert profile.first_name == "Repo"
        assert profile.bio == "Repo bio"
        assert profile.location == "Repo location"

        # Verify database state
        user = User.objects.get(id=user_id)
        assert user.username == "repotest"
        assert user.first_name == "Repo"

        db_profile = UserProfile.objects.get(user_id=user_id)
        assert db_profile.bio == "Repo bio"
        assert db_profile.location == "Repo location"
