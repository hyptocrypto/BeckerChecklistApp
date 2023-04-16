import pytest
import contextlib
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from enum import Enum
from .models import Job, JobItem, StartedJob, CompletedJobItem, CompletedJob, Client
from .views import (
    UpdateStartedJob,
    CreateNewJob,
    DeleteStartedJob,
    StartedJobView,
    UpdateClient,
)
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware


JOB_ITEM_COUNT = 4


class RequestType(Enum):
    GET = 0
    POST = 1


@contextlib.contextmanager
def configure_middleware(request):
    """
    Wrap request with message middleware.
    This is only to avoid errors when calling views that use messages.
    """
    middleware = SessionMiddleware(get_response="")
    middleware.process_request(request)
    request.session.save()
    middleware = MessageMiddleware(get_response="")
    middleware.process_request(request)
    request.session.save()
    yield request


@pytest.mark.django_db
class TestJobs:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Create some default user, and job data"""
        self.client = Client.objects.create(name="TestClient")
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.job = Job.objects.create(name="Test", description="Something")
        self.job_items = [
            JobItem.objects.create(
                job=self.job, name=f"testitem_{i}", description=f"testitem_{i}_info"
            )
            for i in range(JOB_ITEM_COUNT)
        ]

    def _make_request(
        self, url_name: str, kwargs: dict, data: dict, request_type: RequestType
    ):
        """Build request and add user"""
        if request_type == RequestType.GET:
            request = RequestFactory().get(
                reverse(url_name, kwargs=kwargs),
                data=data,
                content_type="application/json",
                HTTP_CONTENT_TYPE="application/json",
            )
        if request_type == RequestType.POST:
            request = RequestFactory().post(
                reverse(url_name, kwargs=kwargs),
                data=data,
                content_type="application/json",
                HTTP_CONTENT_TYPE="application/json",
            )
        request.META["HTTP_REFERER"] = "/"
        request.user = self.user
        return request

    def _start_job(self):
        """Start a new job"""
        request = self._make_request(
            url_name="new_job",
            kwargs={"pk": self.job.pk},
            data={},
            request_type=RequestType.GET,
        )
        with configure_middleware(request):
            CreateNewJob.as_view()(request, self.job.pk)
            new_jobs = StartedJob.objects.all()
            assert len(new_jobs) == 1
            return new_jobs.first()

    def _complete_job_item(self):
        """Start a new job and call the update view to create a completed job item"""
        started_job = self._start_job()
        job_item = self.job_items[0]
        request = self._make_request(
            url_name="update_started_job",
            kwargs={"pk": started_job.pk},
            data={"job_item_id": job_item.pk, "complete": True},
            request_type=RequestType.POST,
        )
        with configure_middleware(request):
            res = UpdateStartedJob.as_view()(request, started_job.pk)
            complete_items = CompletedJobItem.objects.all()
            assert len(complete_items) == 1
            return complete_items.first(), started_job

    def test_client_update(self):
        """Test the update view to update the client name"""
        started_job = self._start_job()
        request = self._make_request(
            url_name="update_client",
            kwargs={"client_name": self.client.name},
            data={},
            request_type=RequestType.POST,
        )
        with configure_middleware(request):
            UpdateClient.as_view()(request, self.client.name)
            assert request.session.get("client_id") == self.client.pk

    def test_notes_update(self):
        """Test the update view to update the notes"""
        started_job = self._start_job()
        request = self._make_request(
            url_name="update_started_job",
            kwargs={"pk": started_job.pk},
            data={"notes": "These are some test notes"},
            request_type=RequestType.POST,
        )
        with configure_middleware(request):
            UpdateStartedJob.as_view()(request, started_job.pk)
            assert StartedJob.objects.first().notes == "These are some test notes"

    def test_update_job_complete_item(self):
        """Test the update view to complete a job item"""
        completed_item, _ = self._complete_job_item()
        assert completed_item.job_item == self.job_items[0]
        assert completed_item.started_job.job == self.job

    def test_update_job_delete_item(self):
        """Test the update view to delete a completed job item"""
        completed_item, started_job = self._complete_job_item()
        request = self._make_request(
            url_name="update_started_job",
            kwargs={"pk": started_job.pk},
            data={"job_item_id": completed_item.pk, "complete": False},
            request_type=RequestType.POST,
        )
        with configure_middleware(request):
            UpdateStartedJob.as_view()(request, started_job.pk)
            assert not CompletedJobItem.objects.all().exists()

    def test_job_complete(self):
        """Test the job detail view to complete the started job"""
        started_job = self._start_job()
        request = self._make_request(
            url_name="job_detail",
            kwargs={"pk": started_job.pk},
            data={},
            request_type=RequestType.POST,
        )
        with configure_middleware(request):
            StartedJobView.as_view()(request, started_job.pk)
            complete_job = CompletedJob.objects.first()
            assert complete_job.started_job == started_job

    def test_delete_job(self):
        """Test the delete started job view"""
        started_job = self._start_job()
        request = self._make_request(
            url_name="delete_job",
            kwargs={"pk": started_job.pk},
            data={},
            request_type=RequestType.GET,
        )
        with configure_middleware(request):
            DeleteStartedJob.as_view()(request, started_job.pk)
            assert not StartedJob.objects.all().exists()
