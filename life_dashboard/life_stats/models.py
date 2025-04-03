from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class LifeStatCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons
    
    class Meta:
        verbose_name = 'Life Stat Category'
        verbose_name_plural = 'Life Stat Categories'
    
    def __str__(self):
        return self.name

class LifeStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='life_stats')
    category = models.ForeignKey(LifeStatCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0)
    target = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)  # e.g., kg, km, hours
    notes = models.TextField(blank=True)
    
    # Tracking
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Life Stat'
        verbose_name_plural = 'Life Stats'
        unique_together = ['user', 'category', 'name']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"
    
    def progress_percentage(self):
        """Calculate progress towards target as percentage"""
        if self.target and self.target != 0:
            return min(100, (self.value / self.target) * 100)
        return 0
