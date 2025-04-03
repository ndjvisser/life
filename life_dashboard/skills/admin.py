from django.contrib import admin
from .models import SkillCategory, Skill

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name', 'description')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'name', 'level', 'experience_points', 'experience_to_next_level')
    list_filter = ('category', 'level')
    search_fields = ('user__username', 'name', 'category__name', 'description')
    readonly_fields = ('created_at', 'last_practiced')
