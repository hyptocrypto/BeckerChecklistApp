from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render
from .models import Job, JobItem, StartedJob, CompletedJob, CompletedJobItem, Client
import json


class _SetClientMixin:
    """
    Mixin to set a client session variable if not set.
    """

    def dispatch(self, request, *args, **kwargs):
        if (
            "client_id" not in request.session
            or not Client.objects.filter(pk=request.session.get("client_id")).exists()
        ):
            request.session["client_id"] = (
                Client.objects.all().order_by("name").first().pk
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_clients = Client.objects.all()
        context["all_clients"] = all_clients
        context["current_client"] = all_clients.get(
            pk=self.request.session.get("client_id")
        )
        return context


class JobListView(LoginRequiredMixin, _SetClientMixin, ListView):
    model = Job
    template_name = "job_list.jinja"
    context_object_name = "jobs"


class CompletedJobListView(LoginRequiredMixin, _SetClientMixin, ListView):
    model = CompletedJob
    template_name = "completed_jobs.jinja"
    context_object_name = "completed_jobs"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CompletedJob.objects.filter(
                started_job__client__pk=self.request.session.get("client_id")
            ).order_by("-created_at")
        # Override the get_queryset method to filter by the current user
        return CompletedJob.objects.filter(
            started_job__client__pk=self.request.session.get("client_id"),
            user=self.request.user,
        ).order_by("-created_at")


class StartedJobListView(LoginRequiredMixin, _SetClientMixin, ListView):
    model = CompletedJob
    template_name = "started_jobs.jinja"
    context_object_name = "jobs"

    def get_queryset(self):
        if self.request.user.is_superuser:
            # All jobs exclude completed jobs
            return StartedJob.objects.filter(
                client__pk=self.request.session.get("client_id")
            ).exclude(
                pk__in=CompletedJob.objects.values_list("started_job_id", flat=True)
            )
        # Override the get_queryset method to filter by the current user and exclude completed jobs
        return StartedJob.objects.filter(
            client__pk=self.request.session.get("client_id"), user=self.request.user
        ).exclude(
            pk__in=CompletedJob.objects.values_list("started_job_id", flat=True).filter(
                user=self.request.user
            )
        )


class UpdateStartedJob(LoginRequiredMixin, _SetClientMixin, View):
    def post(self, request, pk):
        user = request.user
        started_job = StartedJob.objects.get(pk=pk)
        data = json.loads(self.request.body)
        if notes := data.get("notes"):
            started_job.notes = notes
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


class UpdateClient(LoginRequiredMixin, View):
    def post(self, request, client_name):
        client = Client.objects.filter(name=client_name).first()
        if not client:
            raise Exception(f"No client with name: {client_name}")
        request.session["client_id"] = client.pk
        if "/jobs/" in self.request.META["HTTP_REFERER"]:
            return HttpResponseRedirect("/started_jobs")
        if "/job_summary/" in self.request.META["HTTP_REFERER"]:
            return HttpResponseRedirect("/completed_jobs")
        return HttpResponseRedirect(self.request.META["HTTP_REFERER"])


class CreateNewJob(LoginRequiredMixin, _SetClientMixin, View):
    """Create started job and re-route to started job info page"""

    def get(self, request, pk):
        job = Job.objects.get(pk=pk)
        client = Client.objects.get(pk=request.session.get("client_id"))
        started_job = StartedJob.objects.create(
            job=job, user=request.user, client=client
        )
        return HttpResponseRedirect(f"/jobs/{started_job.pk}")


class DeleteStartedJob(LoginRequiredMixin, _SetClientMixin, View):
    def get(self, request, pk):
        try:
            StartedJob.objects.get(pk=pk).delete()
            messages.success(request, "Success! Job deleted!")
            return HttpResponseRedirect("/started_jobs")
        except Exception as e:
            messages.error(request, "Oh no! Error deleting job!")
            return HttpResponseRedirect("/started_jobs")


class CompletedJobSummary(LoginRequiredMixin, _SetClientMixin, TemplateView):
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


class StartedJobView(LoginRequiredMixin, _SetClientMixin, TemplateView):
    """Info page for started job"""

    template_name = "job_detail.jinja"

    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        started_job = StartedJob.objects.get(pk=kwargs.get("pk"))
        context["started_job"] = started_job
        job_items = JobItem.objects.filter(job=started_job.job).all()
        context["job_items"] = job_items
        completed_job_items = CompletedJobItem.objects.values_list(
            "job_item_id", flat=True
        ).filter(user=request.user, started_job=started_job)
        context["completed_job_items"] = completed_job_items
        clients = Client.objects.values_list("name", flat=True).all()
        context["clients"] = [i for i in clients]
        context["current_client"] = (
            started_job.client.name if started_job.client else None
        )
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
