"""
Tests for DjangoUserRepository and related functionality.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.test import TestCase

from ..infrastructure.repositories import DjangoUserRepository


class TestDjangoUserRepository(TestCase):
    """Test suite for DjangoUserRepository."""

    def setUp(self):
        """Set up test data."""
        self.repository = DjangoUserRepository()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="initial_password",
            first_name="Test",
            last_name="User",
        )

    def test_update_user_password_is_hashed(self):
        """Test that password is properly hashed when updating user."""
        new_password = "new_secure_password_123!"

        # Update the user's password
        result = self.repository.update_user(
            user_id=self.user.id, password=new_password
        )

        # Verify the update was successful
        self.assertTrue(result)

        # Refresh the user from the database
        updated_user = get_user_model().objects.get(id=self.user.id)

        # Verify the password was hashed
        self.assertNotEqual(updated_user.password, new_password)
        self.assertTrue(updated_user.check_password(new_password))

        # Verify the password uses a secure hasher
        hasher = identify_hasher(updated_user.password)
        self.assertTrue(
            hasher.safe_summary(updated_user.password)["algorithm"] != "unsalted_sha1"
        )

    def test_update_user_only_updates_whitelisted_fields(self):
        """Test that only whitelisted fields can be updated."""
        # Try to update both whitelisted and non-whitelisted fields
        result = self.repository.update_user(
            user_id=self.user.id,
            first_name="Updated",
            last_name="User",
            is_active=False,
            # Non-whitelisted fields
            is_staff=True,
            is_superuser=True,
        )

        self.assertTrue(result)

        # Refresh the user from the database
        updated_user = get_user_model().objects.get(id=self.user.id)

        # Check whitelisted fields were updated
        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, "User")
        self.assertFalse(updated_user.is_active)

        # Check non-whitelisted fields were not updated
        self.assertFalse(updated_user.is_staff)
        self.assertFalse(updated_user.is_superuser)

    def test_update_user_returns_false_for_nonexistent_user(self):
        """Test that updating a non-existent user returns False."""
        result = self.repository.update_user(
            user_id=99999,  # Non-existent ID
            first_name="Should",
            last_name="Fail",
        )
        self.assertFalse(result)

    def test_update_user_with_no_fields_returns_false(self):
        """Test that updating with no fields returns False."""
        result = self.repository.update_user(user_id=self.user.id)
        self.assertFalse(result)

    def test_update_user_with_invalid_fields_does_nothing(self):
        """Test that invalid fields are ignored during update."""
        original_first_name = self.user.first_name

        result = self.repository.update_user(
            user_id=self.user.id,
            non_existent_field="should_not_be_set",
            another_invalid_field=12345,
        )

        # Should return False because no valid fields were updated
        self.assertFalse(result)

        # Refresh the user and verify no changes were made
        updated_user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, original_first_name)
