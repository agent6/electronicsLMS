from pathlib import Path
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from learning.models import Component, CoreRunWeek, LearningExperience, LearningExperienceSection, Track
from progress.models import LearningProgress, MomentumEvent, XPEvent
from projects.models import BuildLog, Project


class ObsoleteHQSmokeTests(TestCase):
    def make_user(self, username="maker", password="strong-pass-12345", staff=False):
        return get_user_model().objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
            is_staff=staff,
        )

    def make_published_experience(self):
        track = Track.objects.create(number=0, title="Setup", slug="setup", order=0, published=True)
        experience = LearningExperience.objects.create(
            code="001",
            title="Blink the Built-in LED",
            slug="blink-built-in-led",
            track=track,
            content_type=LearningExperience.ContentType.SKILL_LAB,
            difficulty=LearningExperience.Difficulty.BEGINNER,
            estimated_time="20 min",
            summary="Make a tiny light obey your code.",
            hook="Make a tiny light obey your code.",
            student_outcome="Student blinks the onboard LED.",
            status=LearningExperience.Status.PUBLISHED,
            a_la_carte=True,
        )
        LearningExperienceSection.objects.create(
            learning_experience=experience,
            title="Checkpoint",
            order=1,
            section_type=LearningExperienceSection.SectionType.CHECKPOINT,
            body="The LED blinks.",
            published=True,
        )
        return experience

    def test_setup_wizard_appears_when_no_user_exists(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("setup"))
        response = self.client.get(reverse("setup"))
        self.assertContains(response, "Create the first admin account")

    def test_setup_wizard_creates_superuser_and_locks(self):
        response = self.client.post(
            reverse("setup"),
            {
                "display_name": "Admin Maker",
                "email": "admin@example.com",
                "username": "admin",
                "password": "very-strong-admin-pass-123",
                "confirm_password": "very-strong-admin-pass-123",
            },
        )
        self.assertRedirects(response, reverse("learn_dashboard"))
        self.assertTrue(get_user_model().objects.filter(username="admin", is_superuser=True).exists())
        locked = self.client.get(reverse("setup"))
        self.assertEqual(locked.status_code, 404)

    def test_public_pages_load_after_setup(self):
        self.make_user()
        for name in ["home", "safety_center", "parts_index", "debug_index", "tutorials"]:
            response = self.client.get(reverse(name))
            self.assertLess(response.status_code, 500, name)

    def test_authenticated_home_redirects_to_dashboard(self):
        user = self.make_user()
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("learn_dashboard"))

    def test_dashboard_requires_auth(self):
        self.make_user()
        response = self.client.get(reverse("learn_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_login_and_logout_work(self):
        self.make_user(password="strong-pass-12345")
        response = self.client.post(reverse("login"), {"username": "maker", "password": "strong-pass-12345"})
        self.assertRedirects(response, reverse("learn_dashboard"))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))

    def test_dashboard_continue_uses_in_progress_before_core_fallback(self):
        user = self.make_user()
        call_command("seed_obsoletehq", verbosity=0)
        lesson_one = LearningExperience.objects.get(code="001")
        lesson_two = LearningExperience.objects.get(code="002")
        LearningProgress.objects.create(
            user=user,
            learning_experience=lesson_two,
            status=LearningProgress.Status.IN_PROGRESS,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("learn_dashboard"))
        self.assertContains(response, "Continue where you left off")
        self.assertContains(response, lesson_two.title)
        self.assertContains(response, "In progress")
        self.assertNotContains(response, f"<h3 class=\"mt-5 text-xl font-black\">{lesson_one.title}</h3>", html=False)

    def test_dashboard_continue_falls_back_to_next_core_anchor(self):
        user = self.make_user()
        call_command("seed_obsoletehq", verbosity=0)
        lesson_one = LearningExperience.objects.get(code="001")
        self.client.force_login(user)
        response = self.client.get(reverse("learn_dashboard"))
        self.assertContains(response, "Next Core Run lesson")
        self.assertContains(response, lesson_one.title)

    def test_dashboard_stats_show_xp_momentum_logs_and_projects(self):
        user = self.make_user()
        lesson = self.make_published_experience()
        XPEvent.objects.create(user=user, amount=15, reason="Test XP", learning_experience=lesson)
        today = timezone.localdate()
        MomentumEvent.objects.create(user=user, event_type="lesson_complete", meaningful_progress_date=today)
        MomentumEvent.objects.create(user=user, event_type="build_log", meaningful_progress_date=today - timedelta(days=1))
        BuildLog.objects.create(user=user, title="First log", what_built="I made a light blink.")
        Project.objects.create(user=user, title="Desk Light", slug="desk-light", description="A tiny project.")
        self.client.force_login(user)
        response = self.client.get(reverse("learn_dashboard"))
        self.assertContains(response, "15")
        self.assertContains(response, "Momentum streak")
        self.assertContains(response, "First log")
        self.assertContains(response, "Desk Light")
        self.assertContains(response, "Project Passport")

    def test_draft_content_is_hidden_and_published_content_shows(self):
        self.make_user()
        track = Track.objects.create(number=1, title="LEDs", slug="leds", order=1, published=True)
        LearningExperience.objects.create(
            code="002",
            title="Draft Lesson",
            slug="draft-lesson",
            track=track,
            content_type=LearningExperience.ContentType.CONCEPT,
            status=LearningExperience.Status.DRAFT,
        )
        published = self.make_published_experience()
        response = self.client.get(reverse("tutorials"))
        self.assertContains(response, published.title)
        self.assertNotContains(response, "Draft Lesson")
        response = self.client.get(reverse("learning_experience", kwargs={"slug": "draft-lesson"}))
        self.assertEqual(response.status_code, 404)

    def test_seed_creates_week_one_lessons_with_assets_and_code(self):
        user = self.make_user()
        call_command("seed_obsoletehq", verbosity=0)
        experience = LearningExperience.objects.get(code="001")
        self.assertEqual(experience.slug, "meet-your-pico-2-w")
        self.assertEqual(experience.status, LearningExperience.Status.PUBLISHED)
        self.assertTrue(experience.core_anchor)
        self.assertTrue(experience.a_la_carte)
        self.assertEqual(experience.sections.filter(section_type=LearningExperienceSection.SectionType.CODE).count(), 0)

        week_one = CoreRunWeek.objects.get(week_number=1)
        self.assertTrue(week_one.anchor_learning_experiences.filter(pk=experience.pk).exists())

        response = self.client.get(experience.get_absolute_url())
        self.assertContains(response, "Meet Your Pico 2 W")
        self.assertContains(response, "pico_2w_side.png")
        self.assertContains(response, "pico-2-w-pinout.png")
        self.assertContains(response, "Image source:")
        self.assertContains(response, "SunFounder Pico 2 W Starter Kit documentation")
        self.assertContains(response, "https://docs.sunfounder.com/projects/pico-2w-kit/en/latest/introduction_to_pico_2w.html")
        self.assertContains(response, "GPIO pins need 3.3V-safe signals")

        self.client.force_login(user)
        response = self.client.get(reverse("core_run_week", kwargs={"week_number": 1}))
        self.assertContains(response, "Meet Your Pico 2 W")

        expected = [
            ("001", "Meet Your Pico 2 W", "meet-your-pico-2-w"),
            ("002", "Install Thonny", "install-thonny"),
            ("003", "Install MicroPython on the Pico 2 W", "install-micropython-on-the-pico-2-w"),
            ("004", "Blink the Built-in LED", "blink-the-built-in-led"),
        ]
        self.assertEqual(
            list(
                LearningExperience.objects.filter(core_run_week=1, core_anchor=True)
                .order_by("code")
                .values_list("code", "title", "slug")
            ),
            expected,
        )
        for code, title, slug in expected:
            lesson = LearningExperience.objects.get(code=code)
            self.assertEqual(lesson.status, LearningExperience.Status.PUBLISHED)
            response = self.client.get(reverse("learning_experience", kwargs={"slug": slug}))
            self.assertContains(response, title)
            self.assertNotContains(response, "This published lesson needs")

        thonny = self.client.get(reverse("learning_experience", kwargs={"slug": "install-thonny"}))
        self.assertContains(thonny, "download_thonny1.png")
        self.assertContains(thonny, "thonny_ide1.jpg")
        self.assertContains(thonny, "Image source:")

        micropython = self.client.get(reverse("learning_experience", kwargs={"slug": "install-micropython-on-the-pico-2-w"}))
        self.assertContains(micropython, "bootsel_onboard1.png")
        self.assertContains(micropython, "set_pico2w3.png")
        self.assertContains(micropython, "Image source:")

        blink = self.client.get(reverse("learning_experience", kwargs={"slug": "blink-the-built-in-led"}))
        self.assertContains(blink, "from machine import Pin")
        self.assertContains(blink, "led = Pin(&quot;LED&quot;, Pin.OUT)")
        self.assertContains(blink, "built-in LED")
        self.assertNotContains(blink, "wiring_led.png")

    def test_seed_creates_basic_part_pages_with_assets_and_resources(self):
        self.make_user()
        call_command("seed_obsoletehq", verbosity=0)
        expected = {
            "breadboard": (2, 1),
            "jumper-wires": (1, 1),
            "resistor": (4, 2),
            "transistor": (3, 4),
            "capacitor": (1, 3),
            "diode": (1, 3),
            "li-po-charger-module": (3, 2),
            "74hc595": (2, 2),
            "ta6586-motor-driver-chip": (3, 3),
            "led": (2, 4),
            "rgb-led": (4, 2),
            "led-bar-graph": (3, 2),
            "7-segment-display": (2, 2),
            "4-digit-7-segment-display": (2, 2),
            "led-dot-matrix": (3, 2),
            "i2c-lcd1602": (3, 3),
            "ws2812-neopixel-leds": (1, 3),
        }
        for slug, (asset_count, resource_count) in expected.items():
            component = Component.objects.get(slug=slug)
            self.assertIn(component.category, {"Basic", "Chip", "Display"})
            self.assertEqual(component.assets.count(), asset_count)
            self.assertEqual(component.resources.count(), resource_count)
            self.assertTrue(component.source_url)

        response = self.client.get(reverse("part_detail", kwargs={"slug": "li-po-charger-module"}))
        self.assertContains(response, "LTC4054")
        self.assertContains(response, "P1: VBUS, VSYS, GND")
        self.assertContains(response, "sch_lipo_charger.png")
        self.assertContains(response, "Image source:")
        self.assertContains(response, "Diodes Inc: B5819W datasheet")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "resistor"}))
        self.assertContains(response, "Color code card")
        self.assertContains(response, "Wikipedia: Resistor")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "74hc595"}))
        self.assertContains(response, "DS serial data")
        self.assertContains(response, "74hc595_pin.png")
        self.assertContains(response, "Texas Instruments: CD74HC595 datasheet")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "ta6586-motor-driver-chip"}))
        self.assertContains(response, "Input combinations determine stop, forward, reverse, and brake behavior.")
        self.assertContains(response, "TA6586 input truth table")
        self.assertContains(response, "ta6586_priciple.png")
        self.assertContains(response, "Components101: TA6586 datasheet PDF")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "rgb-led"}))
        self.assertContains(response, "common cathode")
        self.assertContains(response, "rgb_pin.jpg")
        self.assertContains(response, "MicroPython: machine.PWM")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "led-dot-matrix"}))
        self.assertContains(response, "788BS")
        self.assertContains(response, "COL pins 13, 3, 4, 10, 6, 11, 15, 16")
        self.assertContains(response, "image85.png")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "i2c-lcd1602"}))
        self.assertContains(response, "PCF8574")
        self.assertContains(response, "Texas Instruments: PCF8574 datasheet")
        self.assertContains(response, "MicroPython: machine.I2C")

        response = self.client.get(reverse("part_detail", kwargs={"slug": "ws2812-neopixel-leds"}))
        self.assertContains(response, "WS2812B")
        self.assertContains(response, "MicroPython: neopixel")

    def test_completion_creates_progress_and_xp(self):
        user = self.make_user()
        experience = self.make_published_experience()
        self.client.force_login(user)
        response = self.client.post(
            reverse("update_learning_progress", kwargs={"slug": experience.slug}),
            {"action": "complete"},
        )
        self.assertRedirects(response, experience.get_absolute_url())
        self.assertTrue(
            LearningProgress.objects.filter(
                user=user,
                learning_experience=experience,
                status=LearningProgress.Status.COMPLETED,
            ).exists()
        )
        self.assertTrue(XPEvent.objects.filter(user=user, learning_experience=experience).exists())

    def test_build_log_belongs_to_correct_user(self):
        owner = self.make_user(username="owner")
        other = self.make_user(username="other")
        log = BuildLog.objects.create(user=owner, title="Private log", what_built="Blink worked")
        self.client.force_login(other)
        response = self.client.get(reverse("build_log_edit", kwargs={"pk": log.pk}))
        self.assertEqual(response.status_code, 404)

    def test_dev_log_form_is_single_quill_body_and_auto_titles(self):
        user = self.make_user()
        lesson = self.make_published_experience()
        self.client.force_login(user)

        response = self.client.get(f"{reverse('build_log_create')}?learning_experience={lesson.pk}")
        self.assertContains(response, 'data-rich-text-editor')
        self.assertContains(response, 'name="what_built"')
        self.assertNotContains(response, 'name="title"')
        self.assertNotContains(response, 'name="what_worked"')
        self.assertNotContains(response, 'name="what_got_weird"')

        response = self.client.post(
            reverse("build_log_create"),
            {
                "learning_experience": str(lesson.pk),
                "what_built": "<p>I learned where the USB port is.</p><script>alert(1)</script>",
            },
        )
        self.assertRedirects(response, reverse("build_log_list"))
        log = BuildLog.objects.get(user=user)
        self.assertTrue(log.title.startswith("Dev Log - "))
        self.assertEqual(log.learning_experience, lesson)
        self.assertIn("<p>I learned where the USB port is.</p>", log.what_built)
        self.assertNotIn("<script", log.what_built)

    def test_project_passport_create_edit_slug_and_ownership(self):
        owner = self.make_user(username="owner")
        other = self.make_user(username="other")
        self.client.force_login(owner)
        response = self.client.get(reverse("project_create"))
        self.assertContains(response, 'data-rich-text-editor')

        response = self.client.post(
            reverse("project_create"),
            {
                "title": "Signal Lamp",
                "description": "<p>A private <strong>project</strong> writeup.</p><script>alert(1)</script>",
                "capstone": "",
            },
        )
        self.assertRedirects(response, reverse("project_list"))
        project = Project.objects.get(user=owner, title="Signal Lamp")
        self.assertEqual(project.slug, "signal-lamp")
        self.assertEqual(project.status, Project.Status.PRIVATE)
        self.assertIn("<strong>project</strong>", project.description)
        self.assertNotIn("<script", project.description)

        response = self.client.post(
            reverse("project_create"),
            {
                "title": "Signal Lamp",
                "description": "A second private project writeup.",
                "capstone": "",
            },
        )
        self.assertRedirects(response, reverse("project_list"))
        self.assertTrue(Project.objects.filter(user=owner, slug="signal-lamp-2").exists())

        response = self.client.post(
            reverse("project_edit", kwargs={"pk": project.pk}),
            {
                "title": "Signal Lamp Remix",
                "description": "Edited notes.",
                "capstone": "on",
            },
        )
        self.assertRedirects(response, reverse("project_list"))
        project.refresh_from_db()
        self.assertEqual(project.slug, "signal-lamp-remix")
        self.assertTrue(project.capstone)

        self.client.force_login(other)
        response = self.client.get(reverse("project_edit", kwargs={"pk": project.pk}))
        self.assertEqual(response.status_code, 404)

    def test_templates_do_not_use_inline_style_attributes_or_style_blocks(self):
        template_root = Path(__file__).resolve().parent.parent / "templates"
        offenders = []
        for path in template_root.rglob("*.html"):
            text = path.read_text()
            if "style=" in text or "<style" in text:
                offenders.append(str(path.relative_to(template_root)))
        self.assertEqual(offenders, [])

# Create your tests here.
