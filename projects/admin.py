from django.contrib import admin

from .models import BuildLog, EvidenceAsset, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "capstone", "updated_at")
    list_filter = ("status", "capstone")
    search_fields = ("title", "description", "user__username")
    filter_horizontal = ("related_learning_experiences",)


@admin.register(BuildLog)
class BuildLogAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "learning_experience", "private", "updated_at")
    list_filter = ("private", "learning_experience")
    search_fields = ("title", "what_built", "user__username")


@admin.register(EvidenceAsset)
class EvidenceAssetAdmin(admin.ModelAdmin):
    list_display = ("user", "build_log", "visibility", "moderation_status", "created_at")
    list_filter = ("visibility", "moderation_status")

# Register your models here.
