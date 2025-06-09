from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a default admin user if one does not exist"

    def handle(self, *args, **options):
        self.stdout.write("Creating default admin user...")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(
                self.style.SUCCESS("Default admin user created successfully!")
            )
        else:
            self.stdout.write(self.style.WARNING("Default admin user already exists"))
