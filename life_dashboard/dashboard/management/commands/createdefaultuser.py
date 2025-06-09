import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Creates a default admin user if one does not exist"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            default=os.getenv("DJANGO_SUPERUSER_USERNAME"),
            help=(
                "Default superuser username (or set DJANGO_SUPERUSER_USERNAME "
                "env var)"
            ),
        )
        parser.add_argument(
            "--email",
            dest="email",
            default=os.getenv("DJANGO_SUPERUSER_EMAIL"),
            help=("Default superuser email (or set DJANGO_SUPERUSER_EMAIL env var)"),
        )
        parser.add_argument(
            "--password",
            dest="password",
            default=os.getenv("DJANGO_SUPERUSER_PASSWORD"),
            help=(
                "Default superuser password (or set DJANGO_SUPERUSER_PASSWORD "
                "env var)"
            ),
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if not username or not email or not password:
            raise CommandError(
                "Username, email, and password must be provided either "
                "via command-line options or "
                "environment variables."
            )

        self.stdout.write(f"Attempting to create default admin user '{username}'...")

        if not User.objects.filter(username=username).exists():
            try:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Default admin user '{username}' created successfully!"
                    )
                )
            except Exception as e:
                raise CommandError(f"Error creating superuser: {e}") from e
        else:
            self.stdout.write(
                self.style.WARNING(f"Default admin user '{username}' already exists")
            )
