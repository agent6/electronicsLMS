from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import redirect, render

from learning.models import Component, CoreRunWeek, Kit, LearningExperience, SafetyWarning


def home(request):
    if request.user.is_authenticated:
        return redirect("learn_dashboard")
    kits = sorted(
        Kit.objects.filter(recommended=True),
        key=lambda kit: (0 if "Pico" in kit.name else 1, kit.name),
    )[:2]
    return render(request, "core/home.html", {"kits": kits})


def health(request):
    try:
        users = get_user_model().objects.count()
    except DatabaseError as exc:
        return JsonResponse({"ok": False, "database": "unavailable", "error": exc.__class__.__name__}, status=503)
    return JsonResponse({"ok": True, "database": "ok", "users": users})


@staff_member_required
def studio(request):
    context = {
        "learning_count": LearningExperience.objects.count(),
        "published_count": LearningExperience.objects.filter(status=LearningExperience.Status.PUBLISHED).count(),
        "kit_count": Kit.objects.count(),
        "component_count": Component.objects.count(),
        "core_week_count": CoreRunWeek.objects.count(),
        "safety_count": SafetyWarning.objects.count(),
    }
    return render(request, "core/studio.html", context)

# Create your views here.
