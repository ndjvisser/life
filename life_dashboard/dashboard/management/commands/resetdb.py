import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, IntegrityError, OperationalError

from life_dashboard.dashboard.utils import reset_database


class Command(BaseCommand):
    help = "Resets the database by dropping all tables and recreating them"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt for confirmation.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Database alias to reset (default: default).",
        )

    def handle(self, *args, **options):
        database = options["database"]
        noinput = options["noinput"]
        auto_confirm = (
            noinput
            or not sys.stdin.isatty()
            or os.getenv("CI", "").lower() in {"1", "true", "yes"}
        )

        if not settings.DEBUG:
            raise CommandError("resetdb can only run when DEBUG is enabled.")
        environment = os.getenv("DJANGO_ENV", "").lower()
        if environment in {"production", "prod", "staging"}:
            self.stderr.write(
                self.style.ERROR(
                    "This command is disabled in production-like environments."
                )
            )
            return

        if not auto_confirm:
            confirmation = input(
                "Are you sure you want to reset the database? "
                "This will delete all data. Type 'yes' to confirm: "
            )

            if confirmation.lower() != "yes":
                self.stdout.write(self.style.ERROR("Database reset aborted."))
                return
        elif not noinput:
            self.stdout.write(
                self.style.WARNING(
                    "Non-interactive environment detected; skipping confirmation."
                )
            )

        self.stdout.write("Resetting the database...")

        try:
            reset_database(database=database)
            self.stdout.write(self.style.SUCCESS("Database reset successfully!"))
        except RuntimeError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
        except (OperationalError, IntegrityError) as exc:
            self.stderr.write(self.style.ERROR(f"Error resetting database: {exc}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {exc}"))
