from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets the database by dropping all tables and recreating them'

    def handle(self, *args, **options):
        self.stdout.write('Resetting the database...')

        with connection.cursor() as cursor:
            cursor.execute('DROP SCHEMA public CASCADE;')
            cursor.execute('CREATE SCHEMA public;')

        self.stdout.write(self.style.SUCCESS('Database reset successfully!')) 