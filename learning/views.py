from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from progress.models import CoreRunProgress, LearningProgress, MomentumEvent, XPEvent
from projects.models import BuildLog, Project

from .models import Component, CoreRunWeek, Kit, LearningExperience, Track


def published_learning():
    return LearningExperience.objects.filter(status=LearningExperience.Status.PUBLISHED)


def momentum_streak_for(user):
    days = list(
        MomentumEvent.objects.filter(user=user)
        .values_list("meaningful_progress_date", flat=True)
        .distinct()
        .order_by("-meaningful_progress_date")
    )
    if not days:
        return 0, None
    streak = 1
    expected = days[0] - timedelta(days=1)
    for day in days[1:]:
        if day == expected:
            streak += 1
            expected = day - timedelta(days=1)
        elif day < expected:
            break
    return streak, days[0]


def next_core_experience_for(user):
    weeks = CoreRunWeek.objects.filter(published=True).prefetch_related("anchor_learning_experiences")
    for week in weeks:
        anchors = week.anchor_learning_experiences.filter(status=LearningExperience.Status.PUBLISHED).order_by("code")
        for experience in anchors:
            progress = LearningProgress.objects.filter(user=user, learning_experience=experience).first()
            if not progress or progress.status != LearningProgress.Status.COMPLETED:
                return experience, week
    return None, weeks.first()


@login_required
def dashboard(request):
    total_xp = request.user.xp_events.aggregate(total=Sum("amount"))["total"] or 0
    recent_progress = LearningProgress.objects.filter(user=request.user).select_related("learning_experience")[:5]
    next_core_experience, next_week = next_core_experience_for(request.user)
    continue_progress = (
        LearningProgress.objects.filter(
            user=request.user,
            status__in=[LearningProgress.Status.IN_PROGRESS, LearningProgress.Status.COME_BACK],
            learning_experience__status=LearningExperience.Status.PUBLISHED,
        )
        .select_related("learning_experience")
        .order_by("-updated_at")
        .first()
    )
    if continue_progress:
        continue_experience = continue_progress.learning_experience
        continue_reason = continue_progress.get_status_display()
    else:
        continue_experience = next_core_experience
        continue_reason = "Next Core Run lesson" if continue_experience else ""
    momentum_streak, last_momentum_date = momentum_streak_for(request.user)
    recent_logs = BuildLog.objects.filter(user=request.user).select_related("learning_experience", "project")[:3]
    recent_projects = Project.objects.filter(user=request.user).prefetch_related("related_learning_experiences")[:3]
    return render(
        request,
        "learning/dashboard.html",
        {
            "total_xp": total_xp,
            "recent": recent_progress,
            "next_week": next_week,
            "continue_experience": continue_experience,
            "continue_reason": continue_reason,
            "published_count": published_learning().count(),
            "build_log_count": request.user.build_logs.count(),
            "momentum_streak": momentum_streak,
            "last_momentum_date": last_momentum_date,
            "recent_logs": recent_logs,
            "recent_projects": recent_projects,
            "project_count": request.user.projects.count(),
        },
    )


def tutorials(request):
    experiences = published_learning().select_related("track").prefetch_related("required_components")
    return render(request, "learning/tutorials.html", {"experiences": experiences, "title": "Tutorials"})


@login_required
def core_run(request):
    weeks = CoreRunWeek.objects.filter(published=True).select_related("track").prefetch_related(
        "anchor_learning_experiences", "optional_bonus_learning_experiences"
    )
    progress_map = {
        item.week_id: item
        for item in CoreRunProgress.objects.filter(user=request.user, week__in=weeks)
    }
    return render(request, "learning/core_run.html", {"weeks": weeks, "progress_map": progress_map})


@login_required
def core_run_week(request, week_number):
    week = get_object_or_404(
        CoreRunWeek.objects.select_related("track").prefetch_related(
            "anchor_learning_experiences", "optional_bonus_learning_experiences"
        ),
        week_number=week_number,
        published=True,
    )
    anchors = week.anchor_learning_experiences.filter(status=LearningExperience.Status.PUBLISHED)
    bonus = week.optional_bonus_learning_experiences.filter(status=LearningExperience.Status.PUBLISHED)
    return render(request, "learning/core_run_week.html", {"week": week, "anchors": anchors, "bonus": bonus})


@login_required
def a_la_carte(request):
    experiences = published_learning().filter(a_la_carte=True).select_related("track").prefetch_related(
        "required_kits", "required_components"
    )
    q = request.GET.get("q", "").strip()
    track = request.GET.get("track", "")
    content_type = request.GET.get("content_type", "")
    difficulty = request.GET.get("difficulty", "")
    kit = request.GET.get("kit", "")
    component = request.GET.get("component", "")
    if q:
        experiences = experiences.filter(Q(title__icontains=q) | Q(summary__icontains=q))
    if track:
        experiences = experiences.filter(track_id=track)
    if content_type:
        experiences = experiences.filter(content_type=content_type)
    if difficulty:
        experiences = experiences.filter(difficulty=difficulty)
    if kit:
        experiences = experiences.filter(required_kits__id=kit)
    if component:
        experiences = experiences.filter(required_components__id=component)
    experiences = experiences.distinct()
    context = {
        "experiences": experiences,
        "tracks": Track.objects.filter(published=True),
        "kits": Kit.objects.all(),
        "components": Component.objects.all(),
        "content_types": LearningExperience.ContentType.choices,
        "difficulties": LearningExperience.Difficulty.choices,
    }
    template = "learning/partials/experience_grid.html" if request.htmx else "learning/a_la_carte.html"
    return render(request, template, context)


def learning_experience_detail(request, slug):
    experience = get_object_or_404(
        published_learning().select_related("track").prefetch_related(
            "required_kits", "required_components", "safety_warnings", "sections"
        ),
        slug=slug,
    )
    progress = None
    if request.user.is_authenticated:
        progress = LearningProgress.objects.filter(user=request.user, learning_experience=experience).first()
    next_item = (
        published_learning()
        .filter(track=experience.track, code__gt=experience.code)
        .order_by("code")
        .first()
    )
    return render(
        request,
        "learning/detail.html",
        {"experience": experience, "progress": progress, "next_item": next_item},
    )


@login_required
def update_learning_progress(request, slug):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    experience = get_object_or_404(published_learning(), slug=slug)
    action = request.POST.get("action")
    status_map = {
        "start": LearningProgress.Status.IN_PROGRESS,
        "complete": LearningProgress.Status.COMPLETED,
        "later": LearningProgress.Status.COME_BACK,
    }
    if action not in status_map:
        return HttpResponseBadRequest("Unknown action")
    progress, _ = LearningProgress.objects.get_or_create(
        user=request.user,
        learning_experience=experience,
    )
    progress.status = status_map[action]
    if action == "complete":
        progress.completed_at = timezone.now()
        XPEvent.objects.get_or_create(
            user=request.user,
            learning_experience=experience,
            reason="Learning experience complete",
            defaults={"amount": 25},
        )
        MomentumEvent.objects.get_or_create(
            user=request.user,
            event_type="lesson_complete",
            meaningful_progress_date=timezone.localdate(),
            notes=experience.title,
        )
    progress.save()
    if request.htmx:
        return render(request, "learning/partials/progress_controls.html", {"experience": experience, "progress": progress})
    return redirect(experience)

# Create your views here.
