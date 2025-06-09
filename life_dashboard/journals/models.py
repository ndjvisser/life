from django.contrib.auth.models import User
from django.db import models


class JournalEntry(models.Model):
    ENTRY_TYPES = [
        ("DAILY", "Daily Reflection"),
        ("WEEKLY", "Weekly Review"),
        ("MILESTONE", "Milestone"),
        ("INSIGHT", "Insight"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="journal_entries"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)

    # Related items
    related_quest = models.ForeignKey(
        "quests.Quest", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_skill = models.ForeignKey(
        "skills.Skill", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_achievement = models.ForeignKey(
        "achievements.Achievement", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Mood and tags
    mood = models.IntegerField(null=True, blank=True)  # 1-10 scale
    tags = models.CharField(max_length=200, blank=True)  # Comma-separated tags

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_entry_type_display()})"

    def get_tags_list(self):
        """Convert comma-separated tags to list"""
        return [tag.strip() for tag in self.tags.split(",")] if self.tags else []
