"""
Tests for dashboard profile queries.
"""

import pytest
from django.contrib.auth import get_user_model

from life_dashboard.dashboard.queries.profile_queries import ProfileQueries
from life_dashboard.shared.queries import get_user_basic_info


@pytest.mark.django_db
class TestProfileQueries:
    """Test cases for profile query functions."""

    def setup_method(self):
        """Set up test data."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_dashboard_user_basic_info_includes_pii(self):
        """Test that dashboard function includes PII for internal use."""
        result = ProfileQueries.get_dashboard_user_basic_info(self.user.id)

        assert result is not None
        assert result["email"] == "test@example.com"  # PII included
        assert result["username"] == "testuser"
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert "full_name" in result
        assert "is_active" in result
        assert "date_joined" in result

    def test_shared_user_basic_info_excludes_pii(self):
        """Test that shared function excludes PII for cross-context safety."""
        result = get_user_basic_info(self.user.id)

        assert result is not None
        assert "email" not in result  # PII excluded
        assert result["username"] == "testuser"
        assert result["first_name"] == "Test"
        assert result["last_name"] == "User"
        assert "user_id" in result
        assert "level" in result
        assert "experience_points" in result

    def test_nonexistent_user_returns_none(self):
        """Test that both functions return None for non-existent users."""
        fake_user_id = 99999

        dashboard_result = ProfileQueries.get_dashboard_user_basic_info(fake_user_id)
        shared_result = get_user_basic_info(fake_user_id)

        assert dashboard_result is None
        assert shared_result is None

    def test_old_function_name_removed(self):
        """Test that the old function name no longer exists."""
        with pytest.raises(AttributeError):
            ProfileQueries.get_user_basic_info(self.user.id)

    def test_function_naming_collision_resolved(self):
        """Test that dashboard and shared functions have different names and behaviors."""
        dashboard_result = ProfileQueries.get_dashboard_user_basic_info(self.user.id)
        shared_result = get_user_basic_info(self.user.id)

        # Both should work but return different data
        assert dashboard_result is not None
        assert shared_result is not None

        # Dashboard includes PII, shared doesn't
        assert "email" in dashboard_result
        assert "email" not in shared_result

        # Different field names/structure
        assert "id" in dashboard_result
        assert "user_id" in shared_result
        assert "user_id" not in dashboard_result
        assert "id" not in shared_result
