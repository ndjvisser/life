from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0002_alter_achievement_tier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="achievement",
            name="tier",
            field=models.CharField(
                choices=[
                    ("BRONZE", "Bronze"),
                    ("SILVER", "Silver"),
                    ("GOLD", "Gold"),
                    ("PLATINUM", "Platinum"),
                ],
                max_length=10,
            ),
        ),
    ]
