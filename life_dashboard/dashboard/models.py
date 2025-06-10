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

    def add_experience(self, points):
        if not isinstance(points, int) or points <= 0:
            raise ValueError("Points must be a positive integer.")
        max_experience = 2**31 - 1
        if self.experience_points + points > max_experience:
            self.experience_points = max_experience
        else:
            self.experience_points += points
        # Simple level calculation: 1000 XP per level
        self.level = max(1, (self.experience_points // 1000) + 1)
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            logger.error(
                f"Error creating profile for user {instance.username}: {str(e)}"
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        logger.warning(f"Profile not found for user {instance.username}, creating one")
        UserProfile.objects.create(user=instance)
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {str(e)}")
