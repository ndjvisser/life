from django.db import models
from django.contrib.auth.models import User

class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons
    
    class Meta:
        verbose_name = 'Skill Category'
        verbose_name_plural = 'Skill Categories'
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
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
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        unique_together = ['user', 'category', 'name']
        ordering = ['-level', '-experience_points']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"
    
    def add_experience(self, amount):
        """Add experience points and handle leveling up"""
        self.experience_points += amount
        
        # Level up if enough experience
        while self.experience_points >= self.experience_to_next_level:
            self.level_up()
        
        self.save()
    
    def level_up(self):
        """Handle leveling up logic"""
        self.level += 1
        self.experience_points -= self.experience_to_next_level
        # Increase experience needed for next level (10% more)
        self.experience_to_next_level = int(self.experience_to_next_level * 1.1)
