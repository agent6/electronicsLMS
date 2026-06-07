from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from accounts import views as account_views
from core import views as core_views
from debugging import views as debugging_views
from learning import views as learning_views
from parts import views as parts_views
from projects import views as project_views
from safety import views as safety_views
from setup_wizard import views as setup_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path("health/", core_views.health, name="health"),
    path("setup/", setup_views.setup, name="setup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", account_views.signup, name="signup"),
    path("verify-email/<uidb64>/<token>/", account_views.verify_email, name="verify_email"),
    path("verify-email/resend/", account_views.resend_verification_email, name="resend_verification_email"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("profile/", account_views.profile, name="profile"),
    path("learn/", learning_views.dashboard, name="learn_dashboard"),
    path("learn/core-run/", learning_views.core_run, name="core_run"),
    path("learn/core-run/week/<int:week_number>/", learning_views.core_run_week, name="core_run_week"),
    path("learn/a-la-carte/", learning_views.a_la_carte, name="a_la_carte"),
    path("tutorials/", learning_views.tutorials, name="tutorials"),
    path("tutorials/<slug:slug>/", learning_views.learning_experience_detail, name="learning_experience"),
    path("tutorials/<slug:slug>/progress/", learning_views.update_learning_progress, name="update_learning_progress"),
    path("parts/", parts_views.parts_index, name="parts_index"),
    path("parts/<slug:slug>/", parts_views.part_detail, name="part_detail"),
    path("debug/", debugging_views.debug_index, name="debug_index"),
    path("debug/<slug:slug>/", debugging_views.debug_detail, name="debug_detail"),
    path("safety/", safety_views.safety_center, name="safety_center"),
    path("projects/", project_views.project_list, name="project_list"),
    path("projects/new/", project_views.project_create, name="project_create"),
    path("projects/<int:pk>/edit/", project_views.project_edit, name="project_edit"),
    path("build-log/", project_views.build_log_list, name="build_log_list"),
    path("build-log/new/", project_views.build_log_create, name="build_log_create"),
    path("build-log/<int:pk>/edit/", project_views.build_log_edit, name="build_log_edit"),
    path("studio/", core_views.studio, name="studio"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
