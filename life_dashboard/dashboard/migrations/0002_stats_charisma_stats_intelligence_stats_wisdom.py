# Generated by Django 5.1.2 on 2024-10-20 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='charisma',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='stats',
            name='intelligence',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='stats',
            name='wisdom',
            field=models.IntegerField(default=5),
        ),
    ]