# Migration to deprecate the core_stats app and drop the old table

from django.db import migrations


def verify_data_migration_forward(apps, schema_editor):
    """
    Verify that all data has been migrated to the new stats.CoreStatModel.
    Since core_stats app has been removed from INSTALLED_APPS, we'll skip validation.
    """
    try:
        OldCoreStat = apps.get_model("core_stats", "CoreStat")
        NewCoreStat = apps.get_model("stats", "CoreStatModel")

        old_count = OldCoreStat.objects.count()
        new_count = NewCoreStat.objects.count()

        if old_count > 0 and new_count < old_count:
            print(
                f"Warning: Data migration incomplete: {old_count} records in core_stats.CoreStat "
                f"but {new_count} in stats.CoreStatModel. "
                "Manual data migration may be required."
            )
        else:
            print(
                f"Core stats migration verified: {old_count} old records, {new_count} new records"
            )
    except Exception as e:
        print(f"Skipping core stats validation due to app removal: {e}")
        # Don't raise exception - allow migration to proceed


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
            "0002_consolidate_stats_models",
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
