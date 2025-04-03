from django.contrib import admin
from .models import Achievement, UserAchievement

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'experience_reward', 'required_level', 'required_skill_level', 'required_quest_completions')
    list_filter = ('tier', 'required_level')
    search_fields = ('name', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('unlocked_at', 'achievement__tier')
    search_fields = ('user__username', 'achievement__name', 'notes')
    readonly_fields = ('unlocked_at',)
