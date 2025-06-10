from django.contrib import admin

from .models import Stats


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "experience", "health", "energy")
    list_filter = ("level",)
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
