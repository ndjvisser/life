from django.contrib import admin

from .models import JournalEntry


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "entry_type", "mood", "created_at")
    list_filter = ("entry_type", "mood", "created_at")
    search_fields = ("user__username", "title", "content", "tags")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user", "related_quest", "related_achievement")
