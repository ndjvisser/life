from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader


def reset_database():
    """Reset the database by dropping all tables and clearing migrations."""
    with connection.cursor() as cursor:
        try:
            # Get all table names and their dependencies
            cursor.execute(
                """
                SELECT name, sql
                FROM sqlite_master
                WHERE type='table'
                AND name NOT IN ('sqlite_sequence', 'django_migrations');
            """
            )
            tables = cursor.fetchall()

            # First disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = OFF;")

            # Drop tables in reverse dependency order
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

            # Reset the database by clearing migrations
            MigrationLoader(connection).reset()
            MigrationExecutor(connection).migrate([])

            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON;")

        except Exception as e:
            raise Exception(f"Error resetting database: {str(e)}") from e
