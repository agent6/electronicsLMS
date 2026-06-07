from html import unescape

import bleach
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from learning.models import LearningExperience

from .models import BuildLog, Project

ALLOWED_RICH_TEXT_TAGS = [
    "a",
    "blockquote",
    "br",
    "em",
    "li",
    "ol",
    "p",
    "span",
    "strong",
    "u",
    "ul",
]
ALLOWED_RICH_TEXT_ATTRIBUTES = {
    "a": ["href", "rel", "target", "title"],
    "li": ["data-list"],
    "span": ["class", "contenteditable"],
}
ALLOWED_RICH_TEXT_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_rich_text(value, required=False):
    cleaned = bleach.clean(
        value or "",
        tags=ALLOWED_RICH_TEXT_TAGS,
        attributes=ALLOWED_RICH_TEXT_ATTRIBUTES,
        protocols=ALLOWED_RICH_TEXT_PROTOCOLS,
        strip=True,
    ).strip()
    plain_text = unescape(strip_tags(cleaned)).replace("\xa0", "").strip()
    if required and not plain_text:
        raise ValidationError("Add a quick note about what you did or learned.")
    return cleaned


class BuildLogForm(forms.ModelForm):
    class Meta:
        model = BuildLog
        fields = ("what_built",)
        widgets = {
            "what_built": forms.Textarea(attrs={"data-rich-text-input": "", "class": "hidden"}),
        }
        labels = {"what_built": "Dev Log"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["what_built"].required = False

    def clean_what_built(self):
        return sanitize_rich_text(self.cleaned_data.get("what_built"), required=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description", "related_learning_experiences", "capstone")
        widgets = {
            "description": forms.Textarea(attrs={"data-rich-text-input": "", "class": "hidden"}),
            "related_learning_experiences": forms.CheckboxSelectMultiple,
        }
        labels = {"description": "Project writeup"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["related_learning_experiences"].queryset = LearningExperience.objects.filter(
            status=LearningExperience.Status.PUBLISHED
        )
        self.fields["related_learning_experiences"].required = False

    def clean_description(self):
        return sanitize_rich_text(self.cleaned_data.get("description"), required=False)
