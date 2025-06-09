from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from quests.models import Habit, Quest


class Command(BaseCommand):
    help = "Creates sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Get the test user
        user = User.objects.get(username="test")

        # Create sample quests
        quests = [
            {
                "title": "Learn Python",
                "description": "Complete a Python course and build a project",
                "quest_type": "one_time",
                "status": "in_progress",
                "experience_reward": 1000,
                "start_date": datetime.now(),
                "due_date": datetime.now() + timedelta(days=30),
            },
            {
                "title": "Read Books",
                "description": "Read one book per month",
                "quest_type": "recurring",
                "status": "active",
                "experience_reward": 500,
                "start_date": datetime.now(),
                "due_date": None,
            },
        ]

        for quest_data in quests:
            Quest.objects.create(user=user, **quest_data)

        # Create sample habits
        habits = [
            {
                "name": "Morning Exercise",
                "description": "30 minutes of exercise every morning",
                "frequency": "daily",
                "target_count": 1,
                "current_streak": 5,
                "longest_streak": 10,
            },
            {
                "name": "Meditation",
                "description": "15 minutes of meditation",
                "frequency": "daily",
                "target_count": 1,
                "current_streak": 3,
                "longest_streak": 7,
            },
            {
                "name": "Weekly Review",
                "description": "Review goals and progress",
                "frequency": "weekly",
                "target_count": 1,
                "current_streak": 2,
                "longest_streak": 4,
            },
        ]

        for habit_data in habits:
            Habit.objects.create(user=user, **habit_data)

        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))
