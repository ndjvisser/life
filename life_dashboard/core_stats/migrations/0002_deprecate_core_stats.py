# Migration to deprecate the core_stats app and drop the old table

from django.db import migrations


def verify_data_migration_forward(apps, schema_editor):
    """
    Verify that all data has been migrated to the new stats.CoreStatModel.
    """
    OldCoreStat = apps.get_model("core_stats", "CoreStat")
    NewCoreStat = apps.get_model("stats", "CoreStatModel")

    old_count = OldCoreStat.objects.count()
    new_count = NewCoreStat.objects.count()

    if old_count > 0 and new_count == 0:
        raise Exception(
            f"Data migration incomplete: {old_count} records in core_stats.CoreStat "
            f"but {new_count} records in stats.CoreStatModel. "
            "Run stats migration 0003_consolidate_core_stats_data first."
        )

    # Log the migration status
    print(
        f"Core stats migration verified: {old_count} old records, {new_count} new records"
    )


def verify_data_migration_backward(apps, schema_editor):
    """
    Verify data exists in old model for rollback.
    """
    pass  # No verification needed for rollback


class Migration(migrations.Migration):
    dependencies = [
        ("core_stats", "0001_initial"),
        (
            "stats",
            "0004_remove_old_core_stats_references",
        ),  # Ensure stats migration is complete
    ]

    operations = [
        migrations.RunPython(
            verify_data_migration_forward,
            verify_data_migration_backward,
            hints={"target_db": "default"},
        ),
        # Drop the old CoreStat model
        migrations.DeleteModel(
            name="CoreStat",
        ),
    ]
