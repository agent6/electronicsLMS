from datetime import timedelta
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Profile
from .tokens import email_verification_token


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class StudentRegistrationTests(TestCase):
    def make_existing_user(self):
        return get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="strong-pass-12345",
        )

    def signup_payload(self, **overrides):
        payload = {
            "username": "student",
            "email": "student@example.com",
            "display_name": "Circuit Starter",
            "password": "strong-pass-12345",
            "confirm_password": "strong-pass-12345",
        }
        payload.update(overrides)
        return payload

    def verification_path_from_latest_email(self):
        body = mail.outbox[-1].body
        start = body.index("http://testserver")
        url = body[start:].split()[0]
        return urlparse(url).path

    def test_signup_redirects_to_setup_until_first_user_exists(self):
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("setup"))

    def test_signup_page_loads_after_first_user_without_age_fields(self):
        self.make_existing_user()
        response = self.client.get(reverse("signup"))
        self.assertContains(response, "Create your account")
        self.assertNotContains(response, "Birthdate")
        self.assertNotContains(response, "Age")

    def test_homepage_start_learning_points_to_signup(self):
        self.make_existing_user()
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'href="{reverse("signup")}"')

    def test_signup_creates_student_profile_sends_email_and_logs_in(self):
        self.make_existing_user()
        response = self.client.post(reverse("signup"), self.signup_payload())
        self.assertRedirects(response, reverse("learn_dashboard"))

        user = get_user_model().objects.get(username="student")
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, "student@example.com")
        self.assertEqual(user.profile.display_name, "Circuit Starter")
        self.assertEqual(user.profile.role, Profile.Role.STUDENT)
        self.assertIsNone(user.profile.email_verified_at)
        self.assertIsNotNone(user.profile.email_verification_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(reverse("verify_email", kwargs={"uidb64": "placeholder", "token": "placeholder"}).split("placeholder")[0], mail.outbox[0].body)

        dashboard = self.client.get(reverse("learn_dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "Verify your private email")

    def test_signup_rejects_duplicate_username_duplicate_email_and_weak_password(self):
        self.make_existing_user()
        get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="strong-pass-12345",
        )
        response = self.client.post(reverse("signup"), self.signup_payload(username="Student", email="OTHER@example.com"))
        self.assertContains(response, "That username is already taken.", status_code=200)

        response = self.client.post(reverse("signup"), self.signup_payload(username="newstudent", email="STUDENT@example.com"))
        self.assertContains(response, "That email is already used.", status_code=200)

        response = self.client.post(
            reverse("signup"),
            self.signup_payload(username="third", email="third@example.com", password="short", confirm_password="short"),
        )
        self.assertContains(response, "This password is too short", status_code=200)

    def test_valid_verification_link_marks_email_verified_and_cannot_be_reused(self):
        self.make_existing_user()
        self.client.post(reverse("signup"), self.signup_payload())
        user = get_user_model().objects.get(username="student")
        path = self.verification_path_from_latest_email()

        response = self.client.get(path)
        self.assertRedirects(response, reverse("learn_dashboard"))
        user.profile.refresh_from_db()
        self.assertIsNotNone(user.profile.email_verified_at)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 400)

    def test_invalid_verification_link_shows_safe_error(self):
        self.make_existing_user()
        response = self.client.get(reverse("verify_email", kwargs={"uidb64": "bad", "token": "bad-token"}))
        self.assertContains(response, "Verification link did not work", status_code=400)

    def test_expired_verification_link_shows_safe_error(self):
        self.make_existing_user()
        self.client.post(reverse("signup"), self.signup_payload())
        path = self.verification_path_from_latest_email()
        original_now = email_verification_token._now
        email_verification_token._now = lambda: original_now() + timedelta(days=4)
        try:
            response = self.client.get(path)
        finally:
            email_verification_token._now = original_now
        self.assertContains(response, "Verification link did not work", status_code=400)

    def test_resend_verification_email_is_hidden_after_verified_and_throttled_before_that(self):
        self.make_existing_user()
        self.client.post(reverse("signup"), self.signup_payload())
        user = get_user_model().objects.get(username="student")
        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post(reverse("resend_verification_email"), {"next": reverse("profile")})
        self.assertRedirects(response, reverse("profile"))
        self.assertEqual(len(mail.outbox), 1)

        profile = user.profile
        profile.email_verification_sent_at = timezone.now() - timedelta(minutes=10)
        profile.save(update_fields=["email_verification_sent_at"])
        response = self.client.post(reverse("resend_verification_email"), {"next": reverse("profile")})
        self.assertRedirects(response, reverse("profile"))
        self.assertEqual(len(mail.outbox), 2)

        path = self.verification_path_from_latest_email()
        self.client.get(path)
        response = self.client.get(reverse("profile"))
        self.assertNotContains(response, "Send verification email")

    def test_password_reset_email_changes_password(self):
        self.make_existing_user()
        get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="strong-pass-12345",
        )
        response = self.client.post(reverse("password_reset"), {"email": "student@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)

        reset_url = mail.outbox[0].body.split("http://testserver", 1)[1].split()[0]
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            response["Location"],
            {"new_password1": "new-strong-pass-12345", "new_password2": "new-strong-pass-12345"},
        )
        self.assertRedirects(response, reverse("password_reset_complete"))

        logged_in = self.client.login(username="student", password="new-strong-pass-12345")
        self.assertTrue(logged_in)
