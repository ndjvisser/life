import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError, OperationalError

from life_dashboard.dashboard.utils import reset_database


class Command(BaseCommand):
    help = "Resets the database by dropping all tables and recreating them"

    def handle(self, *args, **options):
        if not settings.DEBUG and os.getenv("DJANGO_ENV") == "production":
            self.stdout.write(
                self.style.ERROR(
                    "This command cannot be run in a production environment."
                )
            )
            return

        confirmation = input(
            "Are you sure you want to reset the database? "
            "This will delete all data. Type 'yes' to confirm: "
        )

        if confirmation.lower() != "yes":
            self.stdout.write(self.style.ERROR("Database reset aborted."))
            return

        self.stdout.write("Resetting the database...")

        try:
            reset_database()
            self.stdout.write(self.style.SUCCESS("Database reset successfully!"))
        except (OperationalError, IntegrityError) as e:
            self.stdout.write(self.style.ERROR(f"Error resetting database: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
