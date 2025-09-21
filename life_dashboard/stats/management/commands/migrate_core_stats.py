"""
Management command to migrate remaining core stats data from old table to new table.
"""

import sqlite3

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from life_dashboard.stats.models import CoreStatModel

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Migrate remaining core stats data from core_stats_corestat to stats_corestat"
    )

    def handle(self, *args, **options):
        """Migrate core stats data from old table to new table."""

        # Connect to database directly to access old table
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()

        try:
            # Check if old table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='core_stats_corestat'
            """)

            if not cursor.fetchone():
                self.stdout.write(
                    self.style.WARNING(
                        "Old core_stats_corestat table not found. Nothing to migrate."
                    )
                )
                return

            # Get all records from old table
            cursor.execute("SELECT * FROM core_stats_corestat")
            old_records = cursor.fetchall()

            if not old_records:
                self.stdout.write(
                    self.style.WARNING(
                        "No records found in old core_stats_corestat table."
                    )
                )
                return

            # Get column names
            cursor.execute("PRAGMA table_info(core_stats_corestat)")
            columns = [col[1] for col in cursor.fetchall()]

            migrated_count = 0
            skipped_count = 0

            with transaction.atomic():
                for record in old_records:
                    # Create a dictionary from the record
                    record_dict = dict(zip(columns, record, strict=False))

                    try:
                        # Get the user
                        user = User.objects.get(id=record_dict["user_id"])

                        # Check if user already has new core stats
                        if CoreStatModel.objects.filter(user=user).exists():
                            self.stdout.write(
                                self.style.WARNING(
                                    f"User {user.username} already has new core stats, skipping"
                                )
                            )
                            skipped_count += 1
                            continue

                        # Create new core stats record
                        CoreStatModel.objects.create(
                            user=user,
                            strength=record_dict.get("strength", 10),
                            endurance=record_dict.get("endurance", 10),
                            agility=record_dict.get("agility", 10),
                            intelligence=record_dict.get("intelligence", 10),
                            wisdom=record_dict.get("wisdom", 10),
                            charisma=record_dict.get("charisma", 10),
                            experience_points=record_dict.get("experience_points", 0),
                            level=record_dict.get("level", 1),
                        )

                        migrated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Migrated core stats for user {user.username}"
                            )
                        )

                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(
                                f"User with ID {record_dict['user_id']} not found, skipping"
                            )
                        )
                        skipped_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error migrating record {record_dict}: {e}"
                            )
                        )
                        skipped_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Migration completed: {migrated_count} records migrated, {skipped_count} skipped"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during migration: {e}"))
        finally:
            conn.close()
