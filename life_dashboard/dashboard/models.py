import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    experience_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    # Business logic moved to domain layer - use UserService.add_experience() instead
    # This method is deprecated and will be removed
    def add_experience(self, points):
        """
        DEPRECATED: Use UserService.add_experience() instead.
        This method will be removed in a future version.
        """
        import warnings

        warnings.warn(
            "UserProfile.add_experience() is deprecated. Use UserService.add_experience() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Temporary implementation for backward compatibility
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Experience points must be a positive integer.")
        max_experience = 2**31 - 1
        if self.experience_points + points > max_experience:
            self.experience_points = max_experience
        else:
            self.experience_points += points
        # Robust level calculation: 1000 XP per level, minimum level 1
        self.level = max(1, (self.experience_points // 1000) + 1)
        self.save()


# Keep only one signal handler for creating UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created."""
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            logger.error(
                f"Error creating profile for user {instance.username}: {str(e)}"
            )
