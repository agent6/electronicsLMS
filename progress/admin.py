from django.contrib import admin

from .models import BadgeAward, CoreRunProgress, LearningProgress, MomentumEvent, XPEvent


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "learning_experience", "status", "completed_at", "build_log_attached")
    list_filter = ("status", "evidence_submitted", "build_log_attached")
    search_fields = ("user__username", "learning_experience__title", "learning_experience__code")


@admin.register(CoreRunProgress)
class CoreRunProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "week", "status", "completed_at")
    list_filter = ("status", "week")
    search_fields = ("user__username", "week__title")


@admin.register(XPEvent)
class XPEventAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__username", "reason")


@admin.register(MomentumEvent)
class MomentumEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "meaningful_progress_date")
    list_filter = ("event_type",)


@admin.register(BadgeAward)
class BadgeAwardAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "awarded_at")
    list_filter = ("badge",)

# Register your models here.
