"""Utility helpers for the dashboard app."""

import os
from contextlib import contextmanager

from django.conf import settings
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections


@contextmanager
def _sqlite_foreign_keys_disabled(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        yield
    finally:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()


def reset_database(*, db_alias: str = DEFAULT_DB_ALIAS) -> None:
    """Safely reset the configured database.

    The reset operation is only permitted when DEBUG is enabled and the
    ``DJANGO_ENV`` environment variable does not point at a production-like
    environment. The command runs ``flush`` followed by ``migrate`` to rebuild
    schema state without dropping the entire database. For SQLite the routine
    temporarily disables foreign key enforcement to avoid constraint leaks.
    """

    if not settings.DEBUG:
        raise RuntimeError("Database reset is only allowed when DEBUG is True.")

    environment = os.getenv("DJANGO_ENV", "").lower()
    if environment in {"production", "prod", "staging"}:
        raise RuntimeError("Database reset is blocked in production-like environments.")

    connection = connections[db_alias]
    flush_kwargs = {"database": db_alias, "interactive": False, "verbosity": 0}

    if connection.vendor == "sqlite":
        with _sqlite_foreign_keys_disabled(connection):
            call_command("flush", **flush_kwargs)
    else:
        call_command("flush", **flush_kwargs)

    call_command("migrate", database=db_alias, interactive=False, verbosity=0)
