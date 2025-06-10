from django.contrib import admin

from .models import Habit, HabitCompletion, Quest


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "difficulty",
        "quest_type",
        "status",
        "experience_reward",
        "start_date",
        "due_date",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "difficulty",
        "quest_type",
        "status",
        "created_at",
        "start_date",
        "due_date",
    )
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
        "created_at",
        "updated_at",
    )
    list_filter = ("frequency", "created_at")
    search_fields = ("name", "description")
    date_hierarchy = "created_at"


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ("habit", "date", "count", "experience_gained", "notes")
    list_filter = ("habit", "date")
    search_fields = ("habit__name", "notes")
    date_hierarchy = "date"
