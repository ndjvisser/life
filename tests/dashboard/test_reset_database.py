"""Tests for the dashboard database reset helper."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.db import DEFAULT_DB_ALIAS, connections

from life_dashboard.dashboard.utils import reset_database


@pytest.mark.django_db
def test_reset_database_migrates_to_zero_and_reapplies(settings, monkeypatch):
    """Ensure the reset helper migrates to zero before reapplying migrations."""

    settings.DEBUG = True
    monkeypatch.setenv("DJANGO_ENV", "development")

    migrated_apps = {"app_one", "app_two"}

    fake_executor = MagicMock()
    fake_executor.loader.migrated_apps = migrated_apps

    executor_cls = MagicMock(return_value=fake_executor)
    monkeypatch.setattr("life_dashboard.dashboard.utils.MigrationExecutor", executor_cls)

    call_command_mock = MagicMock()
    monkeypatch.setattr("life_dashboard.dashboard.utils.call_command", call_command_mock)

    reset_database()

    executor_cls.assert_called_once_with(connections[DEFAULT_DB_ALIAS])

    expected_zero_targets = [(app_label, None) for app_label in sorted(migrated_apps)]
    fake_executor.migrate.assert_called_once_with(expected_zero_targets)

    call_command_mock.assert_called_once_with(
        "migrate", database=DEFAULT_DB_ALIAS, interactive=False, verbosity=0
    )
