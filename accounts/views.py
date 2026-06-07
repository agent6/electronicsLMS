from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST

from .email import send_verification_email
from .forms import StudentSignupForm
from .models import Profile
from .tokens import email_verification_token


def signup(request):
    if request.user.is_authenticated:
        return redirect("learn_dashboard")
    if not get_user_model().objects.exists():
        return redirect("setup")

    if request.method == "POST":
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            login(request, user)
            messages.success(request, "Account created. Check your email when you are ready to verify.")
            return redirect("learn_dashboard")
    else:
        form = StudentSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is None or not email_verification_token.check_token(user, token):
        return render(request, "accounts/verify_email_result.html", {"verified": False}, status=400)

    profile, _ = Profile.objects.get_or_create(user=user, defaults={"display_name": user.get_username()})
    profile.mark_email_verified()
    messages.success(request, "Email verified. Public publishing can use this account when that feature is available.")

    if request.user.is_authenticated and request.user.pk == user.pk:
        return redirect("learn_dashboard")
    return render(request, "accounts/verify_email_result.html", {"verified": True})


@login_required
@require_POST
def resend_verification_email(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"display_name": request.user.get_username()},
    )
    if profile.email_is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect(request.POST.get("next") or "profile")
    if not request.user.email:
        raise Http404("No email address is attached to this account.")

    resend_seconds = getattr(settings, "EMAIL_VERIFICATION_RESEND_SECONDS", 300)
    if profile.email_verification_sent_at:
        elapsed = timezone.now() - profile.email_verification_sent_at
        if elapsed.total_seconds() < resend_seconds:
            messages.info(request, "Verification email was already sent recently. Check your inbox first.")
            return redirect(request.POST.get("next") or "profile")

    send_verification_email(request, request.user)
    messages.success(request, "Verification email sent.")
    return redirect(request.POST.get("next") or "profile")


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
