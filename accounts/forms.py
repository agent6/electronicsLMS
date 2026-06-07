from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from .models import Profile


class StudentSignupForm(forms.Form):
    username = forms.CharField(max_length=80)
    email = forms.EmailField(label="Private email")
    display_name = forms.CharField(max_length=80)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("That email is already used.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as exc:
                self.add_error("password", exc)
        return cleaned

    def save(self):
        User = get_user_model()
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.display_name = self.cleaned_data["display_name"]
        profile.role = Profile.Role.STUDENT
        profile.email_verified_at = None
        profile.save(update_fields=["display_name", "role", "email_verified_at"])
        return user
