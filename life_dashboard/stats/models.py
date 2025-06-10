from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Stats(models.Model):
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
        verbose_name = "Stats"
        verbose_name_plural = "Stats"

    def __str__(self):
        return f"{self.user.username}'s Stats"

    def gain_experience(self, amount):
        """Gain experience and check for level up."""
        self.experience += amount
        self.check_level_up()
        self.save()

    def check_level_up(self):
        """Check if user should level up based on experience."""
        required_exp = self.level * 1000  # Simple formula: level * 1000
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            return True
        return False


@receiver(post_save, sender=User)
def create_user_stats(sender, instance, created, **kwargs):
    if created:
        try:
            Stats.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating stats for user {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_stats(sender, instance, **kwargs):
    try:
        instance.stats.save()
    except Stats.DoesNotExist:
        print(f"Stats not found for user {instance.username}, creating one")
        Stats.objects.create(user=instance)
    except Exception as e:
        print(f"Error saving stats for user {instance.username}: {str(e)}")
