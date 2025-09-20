from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()

# Constants for experience limits
MAX_EXPERIENCE = 2**31 - 1  # Maximum 32-bit integer
MAX_LEVEL = 100  # Reasonable maximum level


class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Progress tracking
    level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)
    experience_to_next_level = models.IntegerField(default=1000)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_practiced = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        unique_together = ["user", "category", "name"]
        ordering = ["-level", "-experience_points"]

    def __str__(self):
        """Return a human-readable representation of the skill as "<name> (Level <level>)".

        Provides a concise summary used in admin interfaces and logs.
        """
        return f"{self.name} (Level {self.level})"

    # Business logic moved to domain layer - use SkillService instead
    # These methods are deprecated and will be removed
    def add_experience(self, amount):
        """
        Deprecated backward-compatible method to add experience to this Skill.

        Emits a DeprecationWarning advising use of SkillService.add_experience(), then:
        - Validates that `amount` is positive (raises ValidationError if <= 0).
        - Increments `experience_points`, capped at MAX_EXPERIENCE to avoid overflow.
        - Repeatedly calls level_up() while experience_points >= experience_to_next_level and level < MAX_LEVEL.
        - Persists changes by saving the model instance.

        Parameters:
            amount (int): Number of experience points to add.

        Raises:
            ValidationError: If `amount` is not positive (<= 0).
        """
        import warnings

        warnings.warn(
            "Skill.add_experience() is deprecated. Use SkillService.add_experience() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Temporary implementation for backward compatibility
        if amount <= 0:
            raise ValidationError("Experience amount must be positive")

        # Cap experience points to prevent overflow
        new_experience = min(self.experience_points + amount, MAX_EXPERIENCE)
        self.experience_points = new_experience

        # Level up if enough experience and not at max level
        while (
            self.experience_points >= self.experience_to_next_level
            and self.level < MAX_LEVEL
        ):
            self.level_up()

        self.save()

    def level_up(self):
        """
        DEPRECATED: Performs an in-place level up on this Skill instance.

        If the current level is below MAX_LEVEL, increments the skill's level by 1,
        reduces experience_points by the current experience_to_next_level, and increases
        experience_to_next_level by 10% (capped at MAX_EXPERIENCE). Does not persist
        the model (caller must save if required).

        Use SkillService.level_up (domain layer) instead.
        """
        if self.level >= MAX_LEVEL:
            return

        self.level += 1
        self.experience_points -= self.experience_to_next_level
        # Increase experience needed for next level (10% more)
        self.experience_to_next_level = min(
            int(self.experience_to_next_level * 1.1), MAX_EXPERIENCE
        )
