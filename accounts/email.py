from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def build_verification_url(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    path = reverse("verify_email", kwargs={"uidb64": uidb64, "token": token})
    return request.build_absolute_uri(path)


def send_verification_email(request, user):
    profile = user.profile
    verification_url = build_verification_url(request, user)
    context = {
        "user": user,
        "profile": profile,
        "verification_url": verification_url,
        "site_name": get_current_site(request).name,
    }
    subject = render_to_string("accounts/email/verify_email_subject.txt", context).strip()
    text_body = render_to_string("accounts/email/verify_email.txt", context)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.send()
    profile.email_verification_sent_at = timezone.now()
    profile.save(update_fields=["email_verification_sent_at"])
    return verification_url
