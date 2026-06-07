from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "accounts.tokens.EmailVerificationTokenGenerator"

    def check_token(self, user, token):
        if not (user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
            timestamp = base36_to_int(ts_b36)
        except ValueError:
            return False

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(self._make_token_with_timestamp(user, timestamp, secret), token):
                break
        else:
            return False

        timeout = getattr(settings, "EMAIL_VERIFICATION_TIMEOUT", 259200)
        return (self._num_seconds(self._now()) - timestamp) <= timeout

    def _make_hash_value(self, user, timestamp):
        profile = getattr(user, "profile", None)
        verified_at = ""
        if profile and profile.email_verified_at:
            verified_at = profile.email_verified_at.replace(microsecond=0, tzinfo=None)
        email = getattr(user, user.get_email_field_name(), "") or ""
        return f"{user.pk}{user.password}{email}{verified_at}{timestamp}{user.is_active}"


email_verification_token = EmailVerificationTokenGenerator()
