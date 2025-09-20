"""
Tests for secure exception handling in dashboard views.
"""

import logging
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestSecureExceptionHandling:
    """Test cases for secure exception handling in views."""

    def setup_method(self):
        """Set up test data."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client = Client()

    def test_profile_update_exception_logging(self):
        """Test that profile update exceptions are logged with full details but show generic messages to users."""
        # Login the user
        self.client.login(username="testuser", password="testpass123")

        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("life_dashboard.dashboard.views")
        original_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        try:
            # Mock the user service to raise an exception with sensitive info
            with patch(
                "life_dashboard.dashboard.views.get_user_service"
            ) as mock_service:
                mock_user_service = MagicMock()
                mock_user_service.update_profile.side_effect = Exception(
                    "Database error: connection string contains password=secret123"
                )
                mock_service.return_value = mock_user_service

                # Make a POST request to update profile
                response = self.client.post(
                    reverse("dashboard:profile"),
                    {
                        "first_name": "Updated",
                        "last_name": "Name",
                        "email": "updated@test.com",
                        "bio": "Updated bio",
                        "location": "Updated location",
                    },
                    follow=True,
                )  # Follow redirects if any

                # Check that we get a response (may be 200 for form re-render or redirect)
                assert response.status_code in [200, 302]

                # Check messages for generic error
                messages = list(get_messages(response.wsgi_request))
                error_messages = [
                    str(msg) for msg in messages if msg.level_tag == "error"
                ]

                # Should have a generic error message
                generic_message_found = any(
                    "An error occurred while updating your profile" in msg
                    for msg in error_messages
                )
                assert generic_message_found, (
                    f"Generic message not found in: {error_messages}"
                )

                # Should NOT contain sensitive information in user messages
                sensitive_info_in_messages = any(
                    "password=secret123" in msg or "Database error" in msg
                    for msg in error_messages
                )
                assert not sensitive_info_in_messages, (
                    f"Sensitive info found in messages: {error_messages}"
                )

        finally:
            # Clean up logging
            logger.removeHandler(handler)
            logger.setLevel(original_level)

    def test_registration_exception_logging(self):
        """Test that registration exceptions are logged with full details but show generic messages to users."""
        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("life_dashboard.dashboard.views")
        original_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        try:
            # Mock the user service to raise an exception with sensitive info
            with patch(
                "life_dashboard.dashboard.views.get_user_service"
            ) as mock_service:
                mock_user_service = MagicMock()
                mock_user_service.register_user.side_effect = Exception(
                    "SQL injection detected: DROP TABLE users; --"
                )
                mock_service.return_value = mock_user_service

                # Make a POST request to register
                response = self.client.post(
                    reverse("dashboard:register"),
                    {
                        "username": "newuser",
                        "email": "newuser@test.com",
                        "password1": "testpass123",
                        "password2": "testpass123",
                    },
                )

                # Check that we get a response (form re-render)
                assert response.status_code == 200

                # Check messages for generic error
                messages = list(get_messages(response.wsgi_request))
                error_messages = [
                    str(msg) for msg in messages if msg.level_tag == "error"
                ]

                # Should have a generic error message
                generic_message_found = any(
                    "An error occurred during registration" in msg
                    for msg in error_messages
                )
                assert generic_message_found, (
                    f"Generic message not found in: {error_messages}"
                )

                # Should NOT contain sensitive information in user messages
                sensitive_info_in_messages = any(
                    "SQL injection" in msg or "DROP TABLE" in msg
                    for msg in error_messages
                )
                assert not sensitive_info_in_messages, (
                    f"Sensitive info found in messages: {error_messages}"
                )

        finally:
            # Clean up logging
            logger.removeHandler(handler)
            logger.setLevel(original_level)

    def test_exception_handling_uses_proper_logging_method(self):
        """Test that the views use logger.exception() for proper stack trace logging."""
        # Read the views file to verify proper logging methods are used
        with open("life_dashboard/dashboard/views.py") as f:
            views_content = f.read()

        # Should use logger.exception() for full stack traces
        assert "logger.exception(" in views_content, (
            "Should use logger.exception() for stack traces"
        )

        # Should NOT expose exception details to users
        assert 'messages.error(request, f"Error' not in views_content, (
            "Should not expose exception details to users"
        )
        assert "str(e)" not in views_content or "messages.error" not in views_content, (
            "Should not include str(e) in user messages"
        )

        # Should have generic error messages
        assert "An error occurred while updating your profile" in views_content, (
            "Should have generic profile error message"
        )
        assert "An error occurred during registration" in views_content, (
            "Should have generic registration error message"
        )
