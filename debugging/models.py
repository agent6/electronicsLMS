from django.db import models

from learning.models import LearningExperience


class DebugCard(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    symptom = models.CharField(max_length=220)
    what_it_usually_means = models.TextField()
    first_checks = models.TextField()
    fixes = models.TextField()
    safety_warning = models.TextField(blank=True)
    related_learning_experiences = models.ManyToManyField(LearningExperience, blank=True, related_name="debug_cards")
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title

# Create your models here.
