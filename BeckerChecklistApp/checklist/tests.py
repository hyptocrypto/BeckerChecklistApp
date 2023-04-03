import pytest
import json
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

from .models import Job, JobItem, CompletedJob, CompletedJobItem
from .views import JobDetailView


JOB_ITEM_COUNT = 4


@pytest.mark.django_db
class TestJobs:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Create some default user, and job data"""
        self.client = client
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.job = Job.objects.create(name="Test", description="Something")
        self.job_items = [
            JobItem.objects.create(
                job=self.job, name=f"testitem_{i}", description=f"testitem_{i}_info"
            )
            for i in range(JOB_ITEM_COUNT)
        ]

    def test_completed_job_all_items_checked(self):
        """Hit the JobDetail view with data for a completed job with all job items checked"""
        request_body = json.dumps(
            {
                "job_items_data": {
                    f"{i.name}-{i.pk}": True for i in JobItem.objects.all()
                },
                "job_id": f"{self.job.pk}",
            }
        ).encode("utf-8")
        request = RequestFactory().post(
            reverse("job_detail", kwargs={"pk": self.job.pk}),
            data=request_body,
            content_type="application/json",
            HTTP_CONTENT_TYPE="application/json",
        )
        request.user = self.user
        # Hit the view. This will create the completed job and completed job items
        JobDetailView.as_view()(request)
        completed_jobs = CompletedJob.objects.all()
        completed_job_items = CompletedJobItem.objects.all()
        assert len(completed_jobs) == 1
        completed_job = completed_jobs.first()
        assert completed_job.user == self.user
        assert completed_job.check_list_completed

        assert len(completed_job_items) == JOB_ITEM_COUNT
        assert all(j.completed_job == completed_job for j in completed_job_items)

    def test_completed_job_not_all_items_checked(self):
        """Hit the JobDetail view with data for a completed job that does not have all items checked"""
        data = {
            "job_items_data": {f"{i.name}-{i.pk}": True for i in JobItem.objects.all()},
            "job_id": f"{self.job.pk}",
        }
        # Set first job_item in data to false. IE not checked in checklist
        data["job_items_data"][next(iter(data["job_items_data"]))] = False
        request_body = json.dumps(data).encode("utf-8")
        request = RequestFactory().post(
            reverse("job_detail", kwargs={"pk": self.job.pk}),
            data=request_body,
            content_type="application/json",
            HTTP_CONTENT_TYPE="application/json",
        )
        request.user = self.user
        # Hit the view. This will create the completed job and completed job items
        JobDetailView.as_view()(request)
        completed_jobs = CompletedJob.objects.all()
        completed_job_items = CompletedJobItem.objects.all()
        assert len(completed_jobs) == 1
        completed_job = completed_jobs.first()
        assert completed_job.user == self.user
        assert not completed_job.check_list_completed

        assert len(completed_job_items) == JOB_ITEM_COUNT - 1
