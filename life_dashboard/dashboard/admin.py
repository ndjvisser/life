from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "first_name",
        "last_name",
        "email",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "first_name", "last_name", "email")
    readonly_fields = ("created_at", "updated_at")
