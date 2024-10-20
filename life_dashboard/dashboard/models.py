from django.db import models
from django.contrib.auth.models import User


class Stats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=8)
    endurance = models.IntegerField(default=7)

    def __str__(self):
        return f"{self.user.username}'s Stats"