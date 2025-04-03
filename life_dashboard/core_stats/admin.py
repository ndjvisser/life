from django.contrib import admin
from .models import CoreStat

@admin.register(CoreStat)
class CoreStatAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'experience_points', 'strength', 'endurance', 'agility', 'intelligence', 'wisdom', 'charisma')
    list_filter = ('level',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
