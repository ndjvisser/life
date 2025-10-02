"""Tests for the resetdb management command."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.core.management import call_command


@pytest.mark.django_db
@pytest.mark.parametrize("option", ["--using=analytics", "--database=analytics"])
def test_resetdb_command_forwards_using_alias(option, settings, monkeypatch):
    """Ensure the command forwards the provided alias to the helper."""

    settings.DEBUG = True
    monkeypatch.setenv("DJANGO_ENV", "development")

    with patch("life_dashboard.dashboard.management.commands.resetdb.reset_database") as reset:
        call_command("resetdb", "--noinput", option)

    reset.assert_called_once_with(using="analytics")
