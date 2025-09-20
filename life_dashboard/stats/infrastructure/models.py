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
        User, on_delete=models.CASCADE, related_name="core_stats"
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
        """
        Return a human-readable string identifying the user's core stats.

        Returns:
            str: "<username>'s Core Stats" where <username> is the associated user's username.
        """
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
        """
        Return the human-readable name for the life stat category.

        This is used as the model's string representation; it returns the category's `name` field.
        """
        return self.name


class LifeStatModel(models.Model):
    """Django model for life stats - consolidated from life_stats app."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="consolidated_life_stats"
    )
    category = models.ForeignKey(
        LifeStatCategoryModel, on_delete=models.CASCADE, verbose_name="Category"
    )
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
        """
        Return a human-readable representation of the life stat in the format "<username>'s <name>".

        Returns:
            str: Formatted string "<username>'s <name>".
        """
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
        """
        Return a human-readable representation of the stat history entry.

        Format: "<username> - <stat_name>: <old_value> → <new_value>" — useful in admin interfaces and logs.
        """
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
        """
        Return a human-readable representation of the legacy Stats object.

        Returns:
            str: "<username>'s Stats (Legacy)", where username is the related User's username.
        """
        return f"{self.user.username}'s Stats (Legacy)"

    def gain_experience(self, amount):
        """
        DEPRECATED: Increment this legacy Stats instance's experience and trigger level checks.

        Adds the given amount to the instance's `experience`, runs the legacy level-up logic, persists the instance, and emits a DeprecationWarning directing callers to `StatService.add_experience()`. Use the newer StatService API instead of this method.

        Parameters:
            amount (int | float): The amount of experience to add to the current `experience` field.
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
        DEPRECATED: Increment the instance's level while consuming experience points.

        Iteratively subtracts the experience required for the current level (required_exp = level * 1000),
        increments `self.level` for each level up, and deducts the required experience from `self.experience`
        until `self.experience` is less than the requirement for the next level.

        Returns:
            int: Number of levels gained.

        Notes:
            - This method mutates `self.level` and `self.experience` on the instance but does not save the model.
            - Level calculation and progression have been moved to the domain layer; prefer the domain API instead of calling this method.
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
    """
    Post-save signal handler that ensures a legacy Stats record exists for newly created User instances.

    If `created` is True, attempts to create a legacy `Stats` object linked to `instance`. Errors are handled internally and not re-raised.

    Parameters:
        instance (django.contrib.auth.models.User): The User instance that was saved.
        created (bool): True if the save operation created a new User (post_save `created` flag).
    """
    if created:
        try:
            Stats.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating legacy stats for user {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_stats(sender, instance, **kwargs):
    """
    Ensure a legacy Stats record exists for a saved User and persist it for backward compatibility.

    Signal handler intended for Django's post_save on User. If the saved User instance exposes a `stats` attribute, this attempts to save it; if the legacy Stats record is missing it will create one. Errors are caught and reported (printed); the function does not raise.
    Parameters:
        instance: The User instance that was saved.
    """
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
