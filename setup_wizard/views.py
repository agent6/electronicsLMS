from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import Http404
from django.shortcuts import redirect, render

from accounts.models import Profile

from .forms import FirstRunSetupForm


def setup(request):
    User = get_user_model()
    if User.objects.exists():
        raise Http404("Setup is locked.")

    if request.method == "POST":
        form = FirstRunSetupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_superuser(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.display_name = form.cleaned_data["display_name"]
            profile.role = Profile.Role.ADMIN
            profile.save()
            login(request, user)
            messages.success(request, "ObsoleteHQ setup is complete. You are logged in as admin.")
            return redirect("learn_dashboard")
    else:
        form = FirstRunSetupForm()

    return render(request, "setup_wizard/setup.html", {"form": form})

# Create your views here.
