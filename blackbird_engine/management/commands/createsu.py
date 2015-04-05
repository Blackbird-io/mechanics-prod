from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

username = "admin"
email = "admin@blackbirdcreditmarket.com"


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not get_user_model().objects.filter(username=username).exists():
            get_user_model().objects.create_superuser(username, email, "blackbird")