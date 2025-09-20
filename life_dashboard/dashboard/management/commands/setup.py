from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sets up the project by running all necessary commands"

    def handle(self, *args, **options):
        self.stdout.write("Setting up the project...")

        # Reset the database
        self.stdout.write("Resetting the database...")
        try:
            call_command("resetdb")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error resetting database: {e}"))
            return

        # Run migrations
        self.stdout.write("Running migrations...")
        try:
            call_command("makemigrations")
            call_command("migrate")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error running migrations: {e}"))
            return

        # Create superuser
        self.stdout.write("Creating superuser...")
        try:
            call_command("createdefaultuser")
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error creating default admin user: {e}")
            )
            return

        # Create sample data
        self.stdout.write("Creating sample data...")
        try:
            call_command("createsampledata")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error creating sample data: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Project setup completed successfully!"))
