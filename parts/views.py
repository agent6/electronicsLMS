from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from learning.models import Component, LearningExperience


def parts_index(request):
    components = Component.objects.all().prefetch_related("kits", "assets")
    q = request.GET.get("q", "").strip()
    signal = request.GET.get("signal", "")
    if q:
        components = components.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(common_mistakes__icontains=q)
        )
    if signal:
        components = components.filter(signal_type=signal)
    return render(
        request,
        "parts/index.html",
        {"components": components, "signal_types": Component.SignalType.choices},
    )


def part_detail(request, slug):
    component = get_object_or_404(Component.objects.prefetch_related("assets", "resources", "kits"), slug=slug)
    related = component.learning_experiences.filter(status=LearningExperience.Status.PUBLISHED)
    return render(request, "parts/detail.html", {"component": component, "related": related})

# Create your views here.
