from django.contrib import admin
from .models import Quest, Habit, HabitCompletion

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'quest_type', 'status', 'experience_reward', 'due_date')
    list_filter = ('quest_type', 'status')
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'frequency', 'target_count', 'current_streak', 'longest_streak')
    list_filter = ('frequency',)
    search_fields = ('user__username', 'name', 'description')
    readonly_fields = ('created_at', 'last_completed')

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('habit__name', 'notes')
    readonly_fields = ('completed_at',)
