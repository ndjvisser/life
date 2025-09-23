"""Tests for the dashboard's UserProfile model integration with the auth user model."""

from unittest import mock

from django.contrib.auth import get_user_model

from life_dashboard.dashboard.apps import _connect_signals
from life_dashboard.dashboard.models import UserProfile, create_user_profile


def test_user_profile_relates_to_active_user_model():
    """Ensure the UserProfile FK points to the active auth user model."""
    user_field = UserProfile._meta.get_field("user")

    assert user_field.remote_field.model is get_user_model()


@mock.patch("django.db.models.signals.post_save.connect")
def test_signal_connection_uses_runtime_user_model(mock_connect):
    """The signal hookup should resolve the user model at runtime."""
    user_model = get_user_model()

    with mock.patch("django.contrib.auth.get_user_model", return_value=user_model):
        _connect_signals()

    mock_connect.assert_called_with(
        create_user_profile,
        sender=user_model,
        dispatch_uid="life_dashboard.dashboard.create_user_profile",
    )
