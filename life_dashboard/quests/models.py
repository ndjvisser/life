from django.db import models
from django.contrib.auth.models import User

class Quest(models.Model):
    QUEST_TYPES = [
        ('MAIN', 'Main Quest'),
        ('SIDE', 'Side Quest'),
        ('DAILY', 'Daily Quest'),
        ('WEEKLY', 'Weekly Quest'),
        ('ANNUAL', 'Annual Quest'),
    ]
    
    QUEST_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    quest_type = models.CharField(max_length=10, choices=QUEST_TYPES)
    status = models.CharField(max_length=20, choices=QUEST_STATUS, default='NOT_STARTED')
    
    # Quest details
    experience_reward = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quest'
        verbose_name_plural = 'Quests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_quest_type_display()})"

class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    target_count = models.IntegerField(default=1)  # e.g., 3 times per week
    
    # Tracking
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_completed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Habit Completion'
        verbose_name_plural = 'Habit Completions'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.habit.name} completed on {self.completed_at.date()}"
