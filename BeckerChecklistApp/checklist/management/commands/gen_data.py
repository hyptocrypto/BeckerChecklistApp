import random
from checklist.models import Job, JobItem, Client
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.first()
        desc_text = "This is some filler info about a job item"
        Client.objects.create(name="The Millers"),
        Client.objects.create(name="Bob and Jue"),
        Client.objects.create(name="Stratford LLC"),
        Client.objects.create(name="Wellington Reserve"),
        for i in range(5):
            job = Job.objects.create(
                name=f"Test Job {i}",
                description=f"This is the description for Job {i}. This job will include working on things, tracking progress, and billing clients. This is really just some filler text. Please stop reading.",
            )
        for job in Job.objects.all():
            for i in range(8):
                count = random.randint(0, 6)
                bullet_points = [f"* {desc_text}\n" for i in range(count)]
                JobItem.objects.create(
                    job=job,
                    name=f"Job Task {i}",
                    description=f"This is some info about the task. Here are the steps. \n {''.join(bullet_points)}",
                )
