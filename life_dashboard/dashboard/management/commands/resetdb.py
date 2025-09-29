import os
import sys

from django.conf import settings
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, IntegrityError, OperationalError

from life_dashboard.dashboard.utils import reset_database


class Command(BaseCommand):
    help = "Resets the database by migrating to zero and reapplying migrations"

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
            raise CommandError(
                "This command is disabled in production-like environments."
            )

        if not auto_confirm:
            confirmation = input(
                "Are you sure you want to reset the database? "
                "This will delete all data. Type 'yes' to confirm: "
            )

            if confirmation.lower() != "yes":
                raise CommandError("Database reset aborted by user.")
        elif not noinput:
            self.stdout.write(
                self.style.WARNING(
                    "Non-interactive environment detected; skipping confirmation."
                )
            )

        self.stdout.write("Resetting the database...")

        try:
            reset_database(using=database)
            self.stdout.write(self.style.SUCCESS("Database reset successfully!"))
        except RuntimeError as exc:
            message = str(exc)
            self.stderr.write(self.style.ERROR(message))
            raise CommandError(message) from exc
        except (OperationalError, IntegrityError) as exc:
            message = f"Error resetting database: {exc}"
            self.stderr.write(self.style.ERROR(message))
            raise CommandError(message) from exc
        except Exception as exc:
            message = f"An unexpected error occurred: {exc}"
            self.stderr.write(self.style.ERROR(message))
            raise CommandError(message) from exc
