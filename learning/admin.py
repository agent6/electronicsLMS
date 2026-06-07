from django.contrib import admin

from .models import (
    Component,
    ComponentAsset,
    ComponentResource,
    CoreRunWeek,
    Kit,
    LearningExperience,
    LearningExperienceSection,
    SafetyWarning,
    Track,
)


@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ("name", "source_vendor", "recommended")
    list_filter = ("recommended", "source_vendor")
    search_fields = ("name", "description", "notes")
    prepopulated_fields = {"slug": ("name",)}


class ComponentAssetInline(admin.TabularInline):
    model = ComponentAsset
    extra = 1
    fields = ("title", "order", "static_asset_path", "alt_text", "caption", "source_name", "source_url")
    ordering = ("order",)


class ComponentResourceInline(admin.TabularInline):
    model = ComponentResource
    extra = 1
    fields = ("title", "resource_type", "order", "url", "notes")
    ordering = ("order",)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "signal_type", "power_requirement")
    list_filter = ("category", "signal_type", "kits")
    search_fields = ("name", "description", "how_it_is_used", "pins", "pinout_notes", "common_mistakes")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ComponentAssetInline, ComponentResourceInline)
    fieldsets = (
        ("Identity", {"fields": ("name", "slug", "category", "kits", "signal_type")}),
        ("Student-facing content", {"fields": ("description", "how_it_is_used", "common_mistakes", "libraries")}),
        ("Hardware details", {"fields": ("power_requirement", "pins", "pinout_notes", "voltage_notes", "safety_notes")}),
        ("Module internals", {"fields": ("main_component", "discrete_parts", "datasheet_notes")}),
        ("Source and attribution", {"fields": ("source_name", "source_url", "attribution", "image")}),
    )


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "published", "order")
    list_filter = ("published",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("number",)


@admin.register(SafetyWarning)
class SafetyWarningAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "published")
    list_filter = ("severity", "published")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}


class LearningExperienceSectionInline(admin.StackedInline):
    model = LearningExperienceSection
    extra = 1
    fields = (
        "title",
        "order",
        "section_type",
        "body",
        "media",
        "static_asset_path",
        "static_asset_alt",
        "static_asset_caption",
        "static_asset_source_name",
        "static_asset_source_url",
        "published",
    )
    ordering = ("order",)


@admin.register(LearningExperience)
class LearningExperienceAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "track", "content_type", "difficulty", "status", "core_run_week")
    list_filter = ("status", "content_type", "difficulty", "track", "core_anchor", "a_la_carte")
    search_fields = ("code", "title", "summary", "hook", "main_skill")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("required_kits", "required_components", "safety_warnings")
    inlines = (LearningExperienceSectionInline,)
    ordering = ("track__number", "code")
    fieldsets = (
        ("Identity", {"fields": ("code", "title", "slug", "track", "content_type", "difficulty", "status")}),
        ("Student-facing content", {"fields": ("estimated_time", "main_skill", "summary", "hook", "student_outcome", "prerequisites")}),
        ("Parts and safety", {"fields": ("required_kits", "required_components", "safety_level", "safety_warnings")}),
        ("Discovery", {"fields": ("core_run_week", "core_anchor", "a_la_carte", "optional_bonus", "recommended_after_core", "published_at")}),
    )
    readonly_fields = ("published_at",)


@admin.register(CoreRunWeek)
class CoreRunWeekAdmin(admin.ModelAdmin):
    list_display = ("week_number", "title", "track", "published", "estimated_time")
    list_filter = ("published", "track")
    search_fields = ("title", "theme", "goal", "summary")
    filter_horizontal = ("anchor_learning_experiences", "optional_bonus_learning_experiences")
    ordering = ("week_number",)

# Register your models here.
