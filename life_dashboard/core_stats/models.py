from django.db import models
from django.contrib.auth.models import User

class CoreStat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_stats')
    
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
        verbose_name = 'Core Stat'
        verbose_name_plural = 'Core Stats'
    
    def __str__(self):
        return f"{self.user.username}'s Core Stats"
    
    def calculate_level(self):
        """Calculate level based on experience points"""
        # Simple level calculation: every 1000 XP = 1 level
        self.level = (self.experience_points // 1000) + 1
        self.save()
