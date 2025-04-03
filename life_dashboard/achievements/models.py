from django.db import models
from django.contrib.auth.models import User

class Achievement(models.Model):
    TIER_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons
    experience_reward = models.IntegerField(default=0)
    
    # Requirements
    required_level = models.IntegerField(default=1)
    required_skill_level = models.IntegerField(null=True, blank=True)
    required_quest_completions = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        ordering = ['tier', 'required_level']
    
    def __str__(self):
        return f"{self.get_tier_display()} {self.name}"

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} unlocked {self.achievement.name}"
