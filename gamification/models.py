from django.db import models


class Badge(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, default="spark")
    reward_xp = models.PositiveIntegerField(default=0)
    criteria_type = models.CharField(max_length=80, blank=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

# Create your models here.
