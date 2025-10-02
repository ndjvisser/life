"""Utility helpers for the dashboard app."""

import logging
import os

from django.conf import settings
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

logger = logging.getLogger(__name__)


def reset_database(*, using: str = DEFAULT_DB_ALIAS) -> None:
    """Safely reset the configured database.

    The reset operation is only permitted when DEBUG is enabled and the
    ``DJANGO_ENV`` environment variable does not point at a production-like
    environment. The routine leverages Django's migration framework to
    unapply all migrations ("migrate to zero") in a database-agnostic manner
    before reapplying them to rebuild the schema.
    """

    if not settings.DEBUG:
        raise RuntimeError("Database reset is only allowed when DEBUG is True.")

    environment = os.getenv("DJANGO_ENV", "").lower()
    if environment in {"production", "prod", "staging"}:
        raise RuntimeError("Database reset is blocked in production-like environments.")

    connection = connections[using]
    logger.info("Resetting database '%s' by migrating to zero.", using)

    executor = MigrationExecutor(connection)
    migrated_apps = sorted(executor.loader.migrated_apps)
    zero_targets = [(app_label, None) for app_label in migrated_apps]

    if zero_targets:
        executor.migrate(zero_targets)
    else:
        logger.info("No migrated apps detected for database '%s'.", using)

    logger.info("Reapplying migrations for database '%s'.", using)
    call_command("migrate", database=using, interactive=False, verbosity=0)
