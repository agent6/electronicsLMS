from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import DebugCard


def debug_index(request):
    cards = DebugCard.objects.filter(published=True)
    q = request.GET.get("q", "").strip()
    if q:
        cards = cards.filter(
            Q(title__icontains=q)
            | Q(symptom__icontains=q)
            | Q(first_checks__icontains=q)
            | Q(fixes__icontains=q)
        )
    return render(request, "debugging/index.html", {"cards": cards})


def debug_detail(request, slug):
    card = get_object_or_404(DebugCard, slug=slug, published=True)
    return render(request, "debugging/detail.html", {"card": card})

# Create your views here.
