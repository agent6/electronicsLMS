from django.contrib import admin

from .models import Badge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "reward_xp", "criteria_type", "published")
    list_filter = ("published", "criteria_type")
    search_fields = ("name", "description", "criteria_type")
    prepopulated_fields = {"slug": ("name",)}

# Register your models here.
