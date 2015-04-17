from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

email = "admin@blackbirdcreditmarket.com"


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not get_user_model().objects.filter(username=email).exists():
            get_user_model().objects.create_superuser(email, email, "blackbird")