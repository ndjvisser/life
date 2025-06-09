from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from life_dashboard.dashboard.utils import reset_database


class Command(BaseCommand):
    help = "Sets up the project by running all necessary commands"

    def handle(self, *args, **options):
        self.stdout.write("Setting up the project...")

        # Reset the database
        self.stdout.write("Resetting the database...")
        reset_database()

        # Run migrations
        self.stdout.write("Running migrations...")
        call_command("makemigrations")
        call_command("migrate")

        # Create superuser
        self.stdout.write("Creating superuser...")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")

        # Create test user
        self.stdout.write("Creating test user...")
        if not User.objects.filter(username="test").exists():
            User.objects.create_user("test", "test@example.com", "test")

        # Create sample data
        self.stdout.write("Creating sample data...")
        call_command("createsampledata")

        self.stdout.write(self.style.SUCCESS("Project setup completed successfully!"))
