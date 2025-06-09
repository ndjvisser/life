from django.contrib import admin

from .models import Habit, HabitCompletion, Quest


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "quest_type",
        "status",
        "experience_reward",
        "start_date",
        "due_date",
    )
    list_filter = ("quest_type", "status", "user")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "frequency",
        "target_count",
        "current_streak",
        "longest_streak",
    )
    list_filter = ("frequency", "user")
    search_fields = ("name", "description")
    date_hierarchy = "created_at"


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ("habit", "completed_at", "notes")
    list_filter = ("habit", "completed_at")
    search_fields = ("habit__name", "notes")
    date_hierarchy = "completed_at"
