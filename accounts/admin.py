from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("display_name", "user__username", "user__email")

# Register your models here.
