from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from .models import Job, JobItem, StartedJob, CompletedJob, CompletedJobItem
import json


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "job_list.jinja"
    context_object_name = "jobs"


class CompletedJobListView(LoginRequiredMixin, ListView):
    model = CompletedJob
    template_name = "completed_jobs.jinja"
    context_object_name = "completed_jobs"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CompletedJob.objects.all()
        # Override the get_queryset method to filter by the current user
        return CompletedJob.objects.filter(user=self.request.user)


class StartedJobListView(LoginRequiredMixin, ListView):
    model = CompletedJob
    template_name = "started_jobs.jinja"
    context_object_name = "started_jobs"

    def get_queryset(self):
        if self.request.user.is_superuser:
            # All jobs exclude completed jobs
            return StartedJob.objects.all().exclude(
                pk__in=CompletedJob.objects.values_list("started_job_id", flat=True)
            )
        # Override the get_queryset method to filter by the current user and exclude completed jobs
        return StartedJob.objects.filter(user=self.request.user).exclude(
            pk__in=CompletedJob.objects.values_list("started_job_id", flat=True).filter(
                user=self.request.user
            )
        )


class UpdateStartedJob(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        started_job = StartedJob.objects.filter(pk=pk)
        data = json.loads(self.request.body)
        if client_name := data.get("client_name"):
            started_job.update(client_name=client_name)
        if job_item_id := data.get("job_item_id"):
            if data.get("complete"):
                CompletedJobItem.objects.create(
                    started_job=started_job, job_item_id=job_item_id
                )
            if not data.get("complete"):
                completed_job_item = CompletedJobItem.objects.filter(
                    started_job=started_job, job_item_id=job_item_id, user=user
                ).first()
                completed_job_item.delete()
        print(data)
        return HttpResponse(200)


class CreateNewJob(LoginRequiredMixin, View):
    """Create started job and re-route to started job info page"""

    def get(self, request, pk):
        job = Job.objects.get(pk=pk)
        started_job = StartedJob.objects.create(job=job, user=request.user)
        return HttpResponseRedirect(f"/jobs/{started_job.pk}")


class StartedJoblView(LoginRequiredMixin, TemplateView):
    """Info page for started job"""

    template_name = "job_detail.jinja"

    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        self.started_job = StartedJob.objects.get(pk=kwargs.get("pk"))
        context["started_job"] = self.started_job
        job_items = JobItem.objects.filter(job=self.started_job.job).all()
        context["job_items"] = job_items
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(self.request.body)
        # Parse job and out job_items
        job = Job.objects.filter(pk=data.get("job_id")).first()
        job_item_data = data.get("job_items_data").items()
        completed_job_items = JobItem.objects.filter(
            pk__in=[k.split("-")[-1] for k, v in job_item_data if v]
        )
        # Create completed job and items
        completed_job = CompletedJob.objects.create(
            user=user, job=job, check_list_completed=all([v for _, v in job_item_data])
        )
        # Bulk create job items
        CompletedJobItem.objects.bulk_create(
            [
                CompletedJobItem(user=user, completed_job=completed_job, job_item=j)
                for j in completed_job_items
            ]
        )
        return redirect(self.request.path_info)
