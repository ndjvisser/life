# Migration to normalize LifeStat category from CharField to ForeignKey

import django.db.models.deletion
from django.db import migrations, models


def normalize_category_forward(apps, schema_editor):
    """
    Normalize category field from CharField to ForeignKey.
    """
    LifeStatModel = apps.get_model("stats", "LifeStatModel")
    LifeStatCategoryModel = apps.get_model("stats", "LifeStatCategoryModel")

    # Create category records for all distinct category names
    category_mapping = {}
    distinct_categories = LifeStatModel.objects.values_list(
        "category_temp", flat=True
    ).distinct()

    for category_name in distinct_categories:
        if category_name:  # Skip empty/null categories
            category_obj, created = LifeStatCategoryModel.objects.get_or_create(
                name=category_name,
                defaults={
                    "description": f"Auto-created category for {category_name}",
                    "icon": "",
                },
            )
            category_mapping[category_name] = category_obj

    # Update all LifeStat records to use the ForeignKey
    for life_stat in LifeStatModel.objects.all():
        if life_stat.category_temp and life_stat.category_temp in category_mapping:
            life_stat.category = category_mapping[life_stat.category_temp]
            life_stat.save()


def normalize_category_backward(apps, schema_editor):
    """
    Reverse normalization: copy ForeignKey values back to CharField.
    """
    LifeStatModel = apps.get_model("stats", "LifeStatModel")

    # Copy category names back to the temporary field
    for life_stat in LifeStatModel.objects.all():
        if life_stat.category:
            life_stat.category_temp = life_stat.category.name
            life_stat.save()


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0002_consolidate_stats_models"),
    ]

    operations = [
        # Step 1: Add nullable ForeignKey field
        migrations.AddField(
            model_name="lifestatmodel",
            name="category",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="stats.lifestatcategorymodel",
                verbose_name="Category",
            ),
        ),
        # Step 2: Populate the ForeignKey field with data migration
        migrations.RunPython(
            normalize_category_forward,
            normalize_category_backward,
            hints={"target_db": "default"},
        ),
        # Step 3: Make the ForeignKey non-nullable
        migrations.AlterField(
            model_name="lifestatmodel",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="stats.lifestatcategorymodel",
                verbose_name="Category",
            ),
        ),
        # Step 4: Remove the old CharField and update unique constraint
        migrations.AlterUniqueTogether(
            name="lifestatmodel",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="lifestatmodel",
            name="category_temp",
        ),
        # Step 5: Add new unique constraint with ForeignKey
        migrations.AlterUniqueTogether(
            name="lifestatmodel",
            unique_together={("user", "category", "name")},
        ),
    ]
