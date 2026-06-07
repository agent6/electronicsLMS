from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Kit(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    source_vendor = models.CharField(max_length=120, blank=True)
    url = models.URLField(blank=True)
    recommended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to="kits/", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Component(models.Model):
    class SignalType(models.TextChoices):
        DIGITAL = "digital", "Digital"
        ANALOG = "analog", "Analog"
        PWM = "pwm", "PWM"
        I2C = "i2c", "I2C"
        SPI = "spi", "SPI"
        UART = "uart", "UART"
        ONE_WIRE = "one_wire", "One-wire"
        POWER = "power", "Power output"
        OTHER = "other", "Other"

    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80, blank=True)
    kits = models.ManyToManyField(Kit, blank=True, related_name="components")
    description = models.TextField(blank=True)
    how_it_is_used = models.TextField(blank=True)
    signal_type = models.CharField(max_length=24, choices=SignalType.choices, default=SignalType.OTHER)
    power_requirement = models.CharField(max_length=160, blank=True)
    pins = models.CharField(max_length=180, blank=True)
    pinout_notes = models.TextField(blank=True)
    datasheet_notes = models.TextField(blank=True)
    main_component = models.CharField(max_length=160, blank=True)
    discrete_parts = models.TextField(blank=True)
    libraries = models.TextField(blank=True)
    voltage_notes = models.TextField(blank=True)
    safety_notes = models.TextField(blank=True)
    common_mistakes = models.TextField(blank=True)
    source_name = models.CharField(max_length=180, blank=True)
    source_url = models.URLField(blank=True)
    attribution = models.TextField(blank=True)
    image = models.ImageField(upload_to="components/", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ComponentAsset(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name="assets")
    title = models.CharField(max_length=160)
    static_asset_path = models.CharField(max_length=240)
    alt_text = models.CharField(max_length=220)
    caption = models.CharField(max_length=260, blank=True)
    source_name = models.CharField(max_length=180, blank=True)
    source_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.component.name}: {self.title}"


class ComponentResource(models.Model):
    class ResourceType(models.TextChoices):
        SUNFOUNDER = "sunfounder", "SunFounder source"
        DATASHEET = "datasheet", "Datasheet"
        GUIDE = "guide", "Reference guide"
        LIBRARY = "library", "Library / driver"
        OTHER = "other", "Other useful link"

    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=180)
    url = models.URLField()
    resource_type = models.CharField(max_length=24, choices=ResourceType.choices, default=ResourceType.OTHER)
    notes = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "title")

    def __str__(self):
        return f"{self.component.name}: {self.title}"


class Track(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "number")

    def __str__(self):
        return f"Track {self.number}: {self.title}"


class SafetyWarning(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    severity = models.CharField(max_length=40, default="Low")
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("severity", "title")

    def __str__(self):
        return self.title


class LearningExperience(models.Model):
    class ContentType(models.TextChoices):
        CONCEPT = "concept", "Concept Lesson"
        SKILL_LAB = "skill_lab", "Skill Lab"
        GUIDED_BUILD = "guided_build", "Guided Build"
        PROJECT = "project", "Project Tutorial"
        CAPSTONE = "capstone", "Capstone Sprint"
        REFERENCE = "reference", "Reference / Debug Card"

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        BUILDER = "builder", "Builder"
        EXPLORER = "explorer", "Explorer"
        INVENTOR = "inventor", "Inventor"
        ADVANCED = "advanced", "Advanced"

    class SafetyLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        SUPERVISED = "supervised", "Supervised"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "Review"
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        RETIRED = "retired", "Retired"

    code = models.CharField(max_length=12, unique=True)
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    track = models.ForeignKey(Track, on_delete=models.PROTECT, related_name="learning_experiences")
    content_type = models.CharField(max_length=24, choices=ContentType.choices)
    difficulty = models.CharField(max_length=24, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    estimated_time = models.CharField(max_length=80, blank=True)
    required_kits = models.ManyToManyField(Kit, blank=True, related_name="learning_experiences")
    required_components = models.ManyToManyField(Component, blank=True, related_name="learning_experiences")
    main_skill = models.CharField(max_length=160, blank=True)
    prerequisites = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    hook = models.CharField(max_length=220, blank=True)
    student_outcome = models.TextField(blank=True)
    safety_level = models.CharField(max_length=24, choices=SafetyLevel.choices, default=SafetyLevel.LOW)
    safety_warnings = models.ManyToManyField(SafetyWarning, blank=True, related_name="learning_experiences")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    core_run_week = models.PositiveSmallIntegerField(null=True, blank=True)
    core_anchor = models.BooleanField(default=False)
    a_la_carte = models.BooleanField(default=True)
    optional_bonus = models.BooleanField(default=False)
    recommended_after_core = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("track__number", "code")

    def __str__(self):
        return f"{self.code} {self.title}"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    def clean(self):
        if self.status == self.Status.PUBLISHED:
            missing = []
            for field in ("summary", "hook", "student_outcome", "estimated_time"):
                if not getattr(self, field):
                    missing.append(field.replace("_", " "))
            if not self.sections.filter(published=True).exists() and self.pk:
                missing.append("at least one published section")
            if missing:
                raise ValidationError(f"Published learning experiences require {', '.join(missing)}.")

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("learning_experience", kwargs={"slug": self.slug})


class LearningExperienceSection(models.Model):
    class SectionType(models.TextChoices):
        TEXT = "text", "Text"
        PARTS = "parts", "Parts"
        WIRING = "wiring", "Wiring"
        CODE = "code", "Code placeholder"
        CHECKPOINT = "checkpoint", "Checkpoint"
        DEBUG = "debug", "Debug"
        REMIX = "remix", "Remix"
        REFLECTION = "reflection", "Reflection"
        SAFETY = "safety", "Safety"
        MEDIA = "media", "Media"

    learning_experience = models.ForeignKey(
        LearningExperience, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=180)
    order = models.PositiveIntegerField(default=0)
    section_type = models.CharField(max_length=24, choices=SectionType.choices, default=SectionType.TEXT)
    body = models.TextField(blank=True)
    media = models.FileField(upload_to="learning/", blank=True)
    static_asset_path = models.CharField(max_length=240, blank=True)
    static_asset_alt = models.CharField(max_length=220, blank=True)
    static_asset_caption = models.CharField(max_length=260, blank=True)
    static_asset_source_name = models.CharField(max_length=180, blank=True)
    static_asset_source_url = models.URLField(blank=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")
        unique_together = ("learning_experience", "order")

    def __str__(self):
        return f"{self.learning_experience.code} - {self.title}"


class CoreRunWeek(models.Model):
    week_number = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=160)
    track = models.ForeignKey(Track, on_delete=models.PROTECT, related_name="core_run_weeks")
    theme = models.CharField(max_length=160, blank=True)
    goal = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    anchor_learning_experiences = models.ManyToManyField(
        LearningExperience, blank=True, related_name="core_anchor_weeks"
    )
    optional_bonus_learning_experiences = models.ManyToManyField(
        LearningExperience, blank=True, related_name="core_bonus_weeks"
    )
    estimated_time = models.CharField(max_length=80, blank=True)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ("week_number",)

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

# Create your models here.
