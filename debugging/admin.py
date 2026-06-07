from django.contrib import admin

from .models import DebugCard


@admin.register(DebugCard)
class DebugCardAdmin(admin.ModelAdmin):
    list_display = ("title", "symptom", "published")
    list_filter = ("published",)
    search_fields = ("title", "symptom", "what_it_usually_means", "first_checks", "fixes")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_learning_experiences",)

# Register your models here.
