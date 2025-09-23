from django.apps import AppConfig


def _connect_signals():
    """Connect dashboard signal handlers safely during app ready."""
    from django.contrib.auth import get_user_model
    from django.db.models.signals import post_save

    from .models import create_user_profile

    post_save.connect(
        create_user_profile,
        sender=get_user_model(),
        dispatch_uid="life_dashboard.dashboard.create_user_profile",
    )


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "life_dashboard.dashboard"

    def ready(self):
        _connect_signals()
