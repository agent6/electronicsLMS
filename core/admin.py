from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "domain", "setup_completed", "maintenance_mode", "updated_at")

# Register your models here.
