# Generated migration for consolidating core_stats data into stats app

from django.db import migrations


def migrate_core_stats_forward(apps, schema_editor):
    """
    Migrate data from core_stats.CoreStat to stats.CoreStatModel.
    """
    # Get model references
    OldCoreStat = apps.get_model("core_stats", "CoreStat")
    NewCoreStat = apps.get_model("stats", "CoreStatModel")

    # Copy all data from old model to new model
    for old_stat in OldCoreStat.objects.all():
        # Check if user already has consolidated stats (avoid duplicates)
        if not NewCoreStat.objects.filter(user=old_stat.user).exists():
            NewCoreStat.objects.create(
                user=old_stat.user,
                strength=old_stat.strength,
                endurance=old_stat.endurance,
                agility=old_stat.agility,
                intelligence=old_stat.intelligence,
                wisdom=old_stat.wisdom,
                charisma=old_stat.charisma,
                experience_points=old_stat.experience_points,
                level=old_stat.level,
                created_at=old_stat.created_at,
                updated_at=old_stat.updated_at,
            )


def migrate_core_stats_backward(apps, schema_editor):
    """
    Reverse migration: copy data back from stats.CoreStatModel to core_stats.CoreStat.
    """
    # Get model references
    OldCoreStat = apps.get_model("core_stats", "CoreStat")
    NewCoreStat = apps.get_model("stats", "CoreStatModel")

    # Copy data back to old model
    for new_stat in NewCoreStat.objects.all():
        # Check if user already has old stats (avoid duplicates)
        if not OldCoreStat.objects.filter(user=new_stat.user).exists():
            OldCoreStat.objects.create(
                user=new_stat.user,
                strength=new_stat.strength,
                endurance=new_stat.endurance,
                agility=new_stat.agility,
                intelligence=new_stat.intelligence,
                wisdom=new_stat.wisdom,
                charisma=new_stat.charisma,
                experience_points=new_stat.experience_points,
                level=new_stat.level,
                created_at=new_stat.created_at,
                updated_at=new_stat.updated_at,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0002_consolidate_stats_models"),
        ("core_stats", "0001_initial"),  # Ensure core_stats migration exists
    ]

    operations = [
        migrations.RunPython(
            migrate_core_stats_forward,
            migrate_core_stats_backward,
            hints={"target_db": "default"},
        ),
    ]
