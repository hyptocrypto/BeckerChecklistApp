from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Job, JobItem, CompletedJob, CompletedJobItem
import json


class JobListView(ListView):
    model = Job
    template_name = "job_list.jinja"
    context_object_name = "jobs"


class CompletedJobListView(LoginRequiredMixin, ListView):
    model = CompletedJob
    template_name = "completed_jobs.jinja"
    context_object_name = "completed_jobs"
    login_url = "login"  # Specify the login URL for the LoginRequiredMixin

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CompletedJob.objects.all()
        # Override the get_queryset method to filter by the current user
        return CompletedJob.objects.filter(user=self.request.user)


class JobDetailView(DetailView):
    model = Job
    template_name = "job_detail.jinja"
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_job = context.get("job")
        job_items = JobItem.objects.filter(job=current_job).all()
        context["job_items"] = job_items
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = json.loads(self.request.body)
        # Parse job and out job_items
        job = Job.objects.filter(pk=data.get("job_id")).first()
        job_item_data = data.get("job_items_data").items()
        job_items = JobItem.objects.filter(
            pk__in=[k.split("-")[-1] for k, _ in job_item_data]
        )
        # Create completed job and items
        completed_job = CompletedJob.objects.create(
            user=user, job=job, check_list_completed=all([v for _, v in job_item_data])
        )
        # Bulk create job items
        CompletedJobItem.objects.bulk_create(
            [
                CompletedJobItem(user=user, completed_job=completed_job, job_item=j)
                for j in job_items
            ]
        )
        return redirect(self.request.path_info)
