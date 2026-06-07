from django.conf import settings
from django.db import models

from gamification.models import Badge
from learning.models import CoreRunWeek, LearningExperience


class LearningProgress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        COME_BACK = "come_back_later", "Come back later"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_progress")
    learning_experience = models.ForeignKey(LearningExperience, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.NOT_STARTED)
    completed_at = models.DateTimeField(null=True, blank=True)
    evidence_submitted = models.BooleanField(default=False)
    build_log_attached = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "learning_experience")

    def __str__(self):
        return f"{self.user} - {self.learning_experience} - {self.status}"


class CoreRunProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="core_run_progress")
    week = models.ForeignKey(CoreRunWeek, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(max_length=24, choices=LearningProgress.Status.choices, default=LearningProgress.Status.NOT_STARTED)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "week")

    def __str__(self):
        return f"{self.user} - {self.week} - {self.status}"


class XPEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_events")
    amount = models.IntegerField()
    reason = models.CharField(max_length=160)
    learning_experience = models.ForeignKey(LearningExperience, null=True, blank=True, on_delete=models.SET_NULL)
    build_log = models.ForeignKey("projects.BuildLog", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} +{self.amount} {self.reason}"


class MomentumEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="momentum_events")
    event_type = models.CharField(max_length=80)
    meaningful_progress_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-meaningful_progress_date", "-created_at")


class BadgeAward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badge_awards")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awards")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

# Create your models here.
