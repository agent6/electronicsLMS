from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from learning.models import LearningExperience
from progress.models import MomentumEvent, XPEvent

from .forms import BuildLogForm, ProjectForm
from .models import BuildLog, Project


def unique_project_slug(user, title, instance=None):
    base = slugify(title)[:48] or "project"
    slug = base
    index = 2
    existing = Project.objects.filter(user=user, slug=slug)
    if instance is not None:
        existing = existing.exclude(pk=instance.pk)
    while existing.exists():
        suffix = f"-{index}"
        slug = f"{base[: 50 - len(suffix)]}{suffix}"
        index += 1
        existing = Project.objects.filter(user=user, slug=slug)
        if instance is not None:
            existing = existing.exclude(pk=instance.pk)
    return slug


def dev_log_title():
    return f"Dev Log - {timezone.localtime().strftime('%Y-%m-%d %H:%M')}"


def learning_experience_from_request(request):
    learning_experience_id = request.POST.get("learning_experience") or request.GET.get("learning_experience")
    if not learning_experience_id:
        return None
    return LearningExperience.objects.filter(
        pk=learning_experience_id,
        status=LearningExperience.Status.PUBLISHED,
    ).first()


@login_required
def build_log_list(request):
    logs = BuildLog.objects.filter(user=request.user).select_related("learning_experience", "project")
    return render(request, "projects/build_log_list.html", {"logs": logs})


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).prefetch_related("related_learning_experiences")
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.slug = unique_project_slug(request.user, project.title)
            project.status = Project.Status.PRIVATE
            project.save()
            form.save_m2m()
            MomentumEvent.objects.create(
                user=request.user,
                event_type="project_passport",
                meaningful_progress_date=timezone.localdate(),
                notes=project.title,
            )
            return redirect("project_list")
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form, "title": "New Project Passport Entry"})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.slug = unique_project_slug(request.user, project.title, instance=project)
            project.status = Project.Status.PRIVATE
            project.save()
            form.save_m2m()
            return redirect("project_list")
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/project_form.html", {"form": form, "title": "Edit Project Passport Entry"})


@login_required
def build_log_create(request):
    learning_experience = learning_experience_from_request(request)
    if request.method == "POST":
        form = BuildLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.title = dev_log_title()
            log.learning_experience = learning_experience
            log.private = True
            log.save()
            XPEvent.objects.create(user=request.user, amount=10, reason="Build log", build_log=log)
            MomentumEvent.objects.create(
                user=request.user,
                event_type="build_log",
                meaningful_progress_date=timezone.localdate(),
                notes=log.learning_experience.title if log.learning_experience else log.title,
            )
            return redirect("build_log_list")
    else:
        form = BuildLogForm()
    return render(
        request,
        "projects/build_log_form.html",
        {"form": form, "title": "New Dev Log", "learning_experience": learning_experience},
    )


@login_required
def build_log_edit(request, pk):
    log = get_object_or_404(BuildLog, pk=pk, user=request.user)
    if request.method == "POST":
        form = BuildLogForm(request.POST, instance=log)
        if form.is_valid():
            edited_log = form.save(commit=False)
            if not edited_log.title:
                edited_log.title = dev_log_title()
            edited_log.save()
            return redirect("build_log_list")
    else:
        form = BuildLogForm(instance=log)
    return render(request, "projects/build_log_form.html", {"form": form, "title": "Edit Dev Log"})

# Create your views here.
