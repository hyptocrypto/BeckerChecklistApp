from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render
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
            return CompletedJob.objects.all().order_by("-created_at")
        # Override the get_queryset method to filter by the current user
        return CompletedJob.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class StartedJobListView(LoginRequiredMixin, ListView):
    model = CompletedJob
    template_name = "started_jobs.jinja"
    context_object_name = "jobs"

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
        started_job = StartedJob.objects.get(pk=pk)
        data = json.loads(self.request.body)
        if client_name := data.get("client_name"):
            started_job.client_name = client_name
            started_job.save()
        if job_item_id := data.get("job_item_id"):
            if data.get("complete"):
                CompletedJobItem.objects.create(
                    started_job=started_job, job_item_id=job_item_id, user=user
                )
            if not data.get("complete"):
                CompletedJobItem.objects.get(
                    started_job=started_job, job_item_id=job_item_id, user=user
                ).delete()
        return HttpResponse(200)


class CreateNewJob(LoginRequiredMixin, View):
    """Create started job and re-route to started job info page"""

    def get(self, request, pk):
        job = Job.objects.get(pk=pk)
        started_job = StartedJob.objects.create(job=job, user=request.user)
        return HttpResponseRedirect(f"/jobs/{started_job.pk}")


class DeleteStartedJob(LoginRequiredMixin, View):
    def get(self, request, pk):
        try:
            StartedJob.objects.get(pk=pk).delete()
            messages.success(request, "Success! Job deleted!")
            return HttpResponseRedirect("/started_jobs")
        except Exception as e:
            messages.error(request, "Oh no! Error deleting job!")
            return HttpResponseRedirect("/started_jobs")


class CompletedJobSummary(LoginRequiredMixin, TemplateView):
    template_name = "completed_job_summary.jinja"

    def get(self, request, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        completed_job = CompletedJob.objects.get(pk=pk)
        started_job = completed_job.started_job
        context["started_job"] = started_job
        job_items = JobItem.objects.filter(job=started_job.job).all()
        context["job_items"] = job_items
        completed_job_items = CompletedJobItem.objects.values_list(
            "job_item_id", flat=True
        ).filter(user=request.user, started_job=started_job)
        context["completed_job_items"] = completed_job_items
        return render(request, self.template_name, context)


class StartedJobView(LoginRequiredMixin, TemplateView):
    """Info page for started job"""

    template_name = "job_detail.jinja"

    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        self.started_job = StartedJob.objects.get(pk=kwargs.get("pk"))
        context["started_job"] = self.started_job
        job_items = JobItem.objects.filter(job=self.started_job.job).all()
        context["job_items"] = job_items
        completed_job_items = CompletedJobItem.objects.values_list(
            "job_item_id", flat=True
        ).filter(user=request.user, started_job=self.started_job)
        context["completed_job_items"] = completed_job_items
        return render(request, self.template_name, context)

    def post(self, request, pk, **kwargs):
        user = request.user
        job = StartedJob.objects.get(pk=pk)
        CompletedJob.objects.create(
            user=user,
            started_job=job,
            check_list_completed=job.all_items_complete(),
        )
        messages.success(request, "Success! Job Complete!")
        return HttpResponseRedirect("/completed_jobs")
