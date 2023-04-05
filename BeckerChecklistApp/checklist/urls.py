from django.urls import path
from .views import (
    JobListView,
    CompletedJobListView,
    UpdateStartedJob,
    StartedJoblView,
    CreateNewJob,
    StartedJobListView,
    DeleteStartedJob,
)

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("completed_jobs/", CompletedJobListView.as_view(), name="jobs"),
    path("jobs/<int:pk>/", StartedJoblView.as_view(), name="job_detail"),
    path("started_jobs/", StartedJobListView.as_view(), name="started_jobs"),
    path("create_new_job/<int:pk>/", CreateNewJob.as_view(), name="new_job"),
    path("delete_job/<int:pk>/", DeleteStartedJob.as_view(), name="delete_job"),
    path("update_job/<int:pk>/", UpdateStartedJob.as_view(), name="update_started_job"),
]
