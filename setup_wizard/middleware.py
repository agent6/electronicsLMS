from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse


class FirstRunSetupMiddleware:
    allowed_names = {"setup", "health"}
    allowed_prefixes = ("/static/", "/media/", "/favicon.ico")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not get_user_model().objects.exists():
            path = request.path
            try:
                setup_path = reverse("setup")
            except Exception:
                setup_path = "/setup/"
            if path != setup_path and not path.startswith(self.allowed_prefixes):
                return redirect("setup")
        return self.get_response(request)
