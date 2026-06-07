from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Profile


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"display_name": request.user.get_username()},
    )
    if request.method == "POST":
        display_name = request.POST.get("display_name", "").strip()
        if display_name:
            profile.display_name = display_name[:80]
            profile.save()
        return redirect("profile")
    return render(request, "accounts/profile.html", {"profile": profile})

# Create your views here.
