from django.urls import path
from .views import JobDetailView, JobListView, CompletedJobListView

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("completed_jobs/", CompletedJobListView.as_view(), name="jobs"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job_detail"),
]
