from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Quest(models.Model):
    DIFFICULTY_CHOICES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )
    QUEST_TYPES = [
        ("main", "Main Quest"),
        ("side", "Side Quest"),
        ("daily", "Daily Quest"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default="medium"
    )
    quest_type = models.CharField(max_length=10, choices=QUEST_TYPES, default="main")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    experience_reward = models.PositiveIntegerField(default=10)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Habit(models.Model):
    FREQUENCY_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, default="daily"
    )
    target_count = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def complete(self, count=1):
        """Record a habit completion and award experience."""
        from datetime import date

        completion = HabitCompletion.objects.create(
            habit=self, count=count, date=date.today()
        )
        # Award experience based on frequency and count
        experience = {"daily": 10, "weekly": 50, "monthly": 200}.get(
            self.frequency, 10
        ) * count
        self.user.profile.add_experience(experience)
        return completion


class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit, on_delete=models.CASCADE, related_name="completions"
    )
    count = models.IntegerField(default=1)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.habit.name} - {self.date}"
