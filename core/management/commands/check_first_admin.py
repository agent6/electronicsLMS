from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check whether the first-run setup wizard is still required."

    def handle(self, *args, **options):
        User = get_user_model()
        user_count = User.objects.count()
        super_count = User.objects.filter(is_superuser=True).count()
        if user_count == 0:
            self.stdout.write(self.style.WARNING("No users exist. Open /setup/ to create the first admin."))
        elif super_count == 0:
            self.stdout.write(self.style.ERROR("Users exist, but no superuser exists. Use createsuperuser."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Setup locked. {super_count} superuser(s) exist."))
