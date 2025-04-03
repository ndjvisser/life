from django.contrib import admin
from .models import LifeStatCategory, LifeStat

@admin.register(LifeStatCategory)
class LifeStatCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name', 'description')

@admin.register(LifeStat)
class LifeStatAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'name', 'value', 'target', 'unit', 'last_updated')
    list_filter = ('category', 'unit')
    search_fields = ('user__username', 'name', 'category__name')
    readonly_fields = ('created_at', 'last_updated')
