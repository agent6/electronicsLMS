from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="ObsoleteHQ")
    domain = models.CharField(max_length=160, default="obsoletehq.com")
    homepage_primary_cta = models.CharField(max_length=80, default="Start Learning")
    setup_completed = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

# Create your models here.
