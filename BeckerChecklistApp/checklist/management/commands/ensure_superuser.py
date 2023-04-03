from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Exit command if a super user exists
        if User.objects.filter(is_superuser=True).first():
            return
        # Create user
        User.objects.create_superuser(username="admin", password="admin")
