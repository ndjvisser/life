# Generated migration to fix default value for required_quest_completions

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0002_alter_achievement_tier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="achievement",
            name="required_quest_completions",
            field=models.IntegerField(default=1),
        ),
    ]
