from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        MENTOR = "mentor", "Mentor"
        CLUB_LEADER = "club_leader", "Club Leader"
        CONTENT_AUTHOR = "content_author", "Content Author"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def email_is_verified(self):
        return self.email_verified_at is not None

    def mark_email_verified(self):
        if not self.email_verified_at:
            self.email_verified_at = timezone.now()
            self.save(update_fields=["email_verified_at"])

    def __str__(self):
        return self.display_name or self.user.get_username()

# Create your models here.
