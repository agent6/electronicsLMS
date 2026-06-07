from django.conf import settings
from django.db import models

from learning.models import LearningExperience


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PRIVATE = "private", "Private"
        MENTOR_VISIBLE = "mentor_visible", "Mentor-visible"
        PUBLISHED = "published", "Published"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=180)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PRIVATE)
    related_learning_experiences = models.ManyToManyField(LearningExperience, blank=True, related_name="projects")
    capstone = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "slug")
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title


class BuildLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="build_logs")
    title = models.CharField(max_length=180)
    learning_experience = models.ForeignKey(
        LearningExperience, null=True, blank=True, on_delete=models.SET_NULL, related_name="build_logs"
    )
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="build_logs")
    what_built = models.TextField()
    what_worked = models.TextField(blank=True)
    what_got_weird = models.TextField(blank=True)
    what_changed = models.TextField(blank=True)
    what_next = models.TextField(blank=True)
    private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title


class EvidenceAsset(models.Model):
    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        MENTOR_VISIBLE = "mentor_visible", "Mentor-visible"

    class ModerationStatus(models.TextChoices):
        NOT_NEEDED = "not_needed", "Not needed"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evidence_assets")
    build_log = models.ForeignKey(BuildLog, null=True, blank=True, on_delete=models.CASCADE, related_name="evidence_assets")
    file = models.FileField(upload_to="evidence/", blank=True)
    caption = models.CharField(max_length=220, blank=True)
    visibility = models.CharField(max_length=24, choices=Visibility.choices, default=Visibility.PRIVATE)
    moderation_status = models.CharField(max_length=24, choices=ModerationStatus.choices, default=ModerationStatus.NOT_NEEDED)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
