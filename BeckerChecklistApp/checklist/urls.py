from django.urls import path
from .views import (
    JobListView,
    CompletedJobListView,
    UpdateStartedJob,
    StartedJoblView,
    CreateNewJob,
    StartedJobListView,
    DeleteStartedJob,
    CompletedJobSummary,
)

urlpatterns = [
    path("", JobListView.as_view(), name="jobs"),
    path("completed_jobs/", CompletedJobListView.as_view(), name="jobs"),
    path("started_jobs/", StartedJobListView.as_view(), name="started_jobs"),
    path("jobs/<int:pk>/", StartedJoblView.as_view(), name="job_detail"),
    path("job_summary/<int:pk>/", CompletedJobSummary.as_view(), name="job_summary"),
    path("create_new_job/<int:pk>/", CreateNewJob.as_view(), name="new_job"),
    path("delete_job/<int:pk>/", DeleteStartedJob.as_view(), name="delete_job"),
    path("update_job/<int:pk>/", UpdateStartedJob.as_view(), name="update_started_job"),
]
