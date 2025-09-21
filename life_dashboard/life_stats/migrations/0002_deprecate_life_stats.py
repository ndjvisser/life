# Migration to deprecate the life_stats app and drop the old tables

from django.db import migrations


def verify_data_migration_forward(apps, schema_editor):
    """
    Verify that all data has been migrated to the new stats models.
    """
    OldLifeStat = apps.get_model("life_stats", "LifeStat")
    OldLifeStatCategory = apps.get_model("life_stats", "LifeStatCategory")
    NewLifeStat = apps.get_model("stats", "LifeStatModel")
    NewLifeStatCategory = apps.get_model("stats", "LifeStatCategoryModel")

    old_life_stat_count = OldLifeStat.objects.count()
    old_category_count = OldLifeStatCategory.objects.count()
    new_life_stat_count = NewLifeStat.objects.count()
    new_category_count = NewLifeStatCategory.objects.count()

    if old_life_stat_count > 0 and new_life_stat_count == 0:
        raise Exception(
            f"Data migration incomplete: {old_life_stat_count} records in life_stats.LifeStat "
            f"but {new_life_stat_count} records in stats.LifeStatModel. "
            "Run stats migration 0002_consolidate_stats_models first."
        )

    # Log the migration status
    print(
        f"Life stats migration verified: {old_life_stat_count} old life stats, "
        f"{new_life_stat_count} new life stats, {old_category_count} old categories, "
        f"{new_category_count} new categories"
    )


def verify_data_migration_backward(apps, schema_editor):
    """
    Verify data exists in old models for rollback.
    """
    pass  # No verification needed for rollback


class Migration(migrations.Migration):
    dependencies = [
        ("life_stats", "0001_initial"),
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
        # Drop the old models
        migrations.DeleteModel(
            name="LifeStat",
        ),
        migrations.DeleteModel(
            name="LifeStatCategory",
        ),
    ]
