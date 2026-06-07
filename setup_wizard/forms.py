from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError


class FirstRunSetupForm(forms.Form):
    display_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    username = forms.CharField(max_length=80, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")
        email = cleaned.get("email")
        username = cleaned.get("username") or email
        User = get_user_model()

        if password and confirm and password != confirm:
            self.add_error("confirm_password", "Passwords do not match.")
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as exc:
                self.add_error("password", exc)
        if username and User.objects.filter(username=username).exists():
            self.add_error("username", "That username is already taken.")
        if email and User.objects.filter(email=email).exists():
            self.add_error("email", "That email is already used.")
        cleaned["username"] = username
        return cleaned
