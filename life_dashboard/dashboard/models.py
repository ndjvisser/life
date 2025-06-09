import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


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


class Stats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=8)
    endurance = models.IntegerField(default=7)
    intelligence = models.IntegerField(default=5)
    charisma = models.IntegerField(default=5)
    wisdom = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.user.username}'s Stats"
