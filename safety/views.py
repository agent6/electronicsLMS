from django.shortcuts import render

from learning.models import SafetyWarning


def safety_center(request):
    warnings = SafetyWarning.objects.filter(published=True)
    return render(request, "safety/center.html", {"warnings": warnings})

# Create your views here.
