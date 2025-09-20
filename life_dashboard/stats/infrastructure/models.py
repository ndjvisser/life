"""
Stats infrastructure models - Django ORM models for persistence.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class CoreStatModel(models.Model):
    """Django model for core RPG stats - consolidated from core_stats app."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="consolidated_core_stats"
    )

    # RPG-style attributes
    strength = models.IntegerField(default=10)
    endurance = models.IntegerField(default=10)
    agility = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    charisma = models.IntegerField(default=10)

    # Experience and level
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "stats"
        verbose_name = "Core Stat"
        verbose_name_plural = "Core Stats"
        db_table = "stats_corestat"  # Use consistent table name

    def __str__(self):
        return f"{self.user.username}'s Core Stats"


class LifeStatCategoryModel(models.Model):
    """Django model for life stat categories."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons

    class Meta:
        app_label = "stats"
        verbose_name = "Life Stat Category"
        verbose_name_plural = "Life Stat Categories"
        db_table = "stats_lifestatcategory"

    def __str__(self):
        return self.name


class LifeStatModel(models.Model):
    """Django model for life stats - consolidated from life_stats app."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="consolidated_life_stats"
    )
    category = models.CharField(max_length=50)  # health, wealth, relationships
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)  # e.g., kg, km, hours
    notes = models.TextField(blank=True)

    # Tracking
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "stats"
        verbose_name = "Life Stat"
        verbose_name_plural = "Life Stats"
        unique_together = ["user", "category", "name"]
        db_table = "stats_lifestat"

    def __str__(self):
        return f"{self.user.username}'s {self.name}"


class StatHistoryModel(models.Model):
    """Django model for tracking stat changes over time."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="stat_history"
    )
    stat_type = models.CharField(max_length=20)  # 'core' or 'life'
    stat_name = models.CharField(max_length=100)  # e.g., 'strength' or 'health.weight'
    old_value = models.DecimalField(max_digits=10, decimal_places=2)
    new_value = models.DecimalField(max_digits=10, decimal_places=2)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)
    change_reason = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "stats"
        verbose_name = "Stat History"
        verbose_name_plural = "Stat Histories"
        db_table = "stats_stathistory"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "stat_type", "stat_name"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.stat_name}: {self.old_value} → {self.new_value}"


# Legacy Stats model for backward compatibility
class Stats(models.Model):
    """
    DEPRECATED: Legacy stats model for backward compatibility.
    Use CoreStatModel instead. This will be removed in a future version.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="stats")
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    health = models.IntegerField(default=100)
    energy = models.IntegerField(default=100)
    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=8)
    endurance = models.IntegerField(default=7)
    intelligence = models.IntegerField(default=5)
    charisma = models.IntegerField(default=5)
    wisdom = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "stats"
        verbose_name = "Stats (Legacy)"
        verbose_name_plural = "Stats (Legacy)"

    def __str__(self):
        return f"{self.user.username}'s Stats (Legacy)"

    def gain_experience(self, amount):
        """
        DEPRECATED: Use StatService.add_experience() instead.
        """
        import warnings

        warnings.warn(
            "Stats.gain_experience() is deprecated. Use StatService.add_experience() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.experience += amount
        self.check_level_up()
        self.save()

    def check_level_up(self):
        """
        DEPRECATED: Level calculation moved to domain layer.
        """
        levels_gained = 0
        while True:
            required_exp = self.level * 1000  # Simple formula: level * 1000
            if self.experience >= required_exp:
                self.level += 1
                self.experience -= required_exp
                levels_gained += 1
            else:
                break
        return levels_gained


# Signal handlers for backward compatibility
@receiver(post_save, sender=User)
def create_user_stats(sender, instance, created, **kwargs):
    """Create legacy stats for backward compatibility."""
    if created:
        try:
            Stats.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating legacy stats for user {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_stats(sender, instance, **kwargs):
    """Save legacy stats for backward compatibility."""
    try:
        if hasattr(instance, "stats"):
            instance.stats.save()
    except Stats.DoesNotExist:
        print(f"Legacy stats not found for user {instance.username}, creating one")
        try:
            Stats.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating legacy stats: {str(e)}")
    except Exception as e:
        print(f"Error saving legacy stats for user {instance.username}: {str(e)}")
