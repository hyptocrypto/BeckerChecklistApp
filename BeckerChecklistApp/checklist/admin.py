from checklist.gcp import gcp_storage_sync
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Job, JobItem, CompletedJob, Client, StartedJob

class AdminModel(admin.ModelAdmin):
    """ModelAdmin sub class to call gcp sync after bulk deletes and updates."""
    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        ret =  super().delete_queryset(request, queryset)
        gcp_storage_sync()


class JobItemInline(admin.StackedInline):
    model = JobItem
    fk_name = "job"  # specify the foreign key field name for the relationship
    extra = 1


@admin.register(Job)
class JobAdmin(AdminModel):
    inlines = [JobItemInline]


@admin.register(JobItem)
class JobItemAdmin(AdminModel):
    pass


@admin.register(CompletedJob)
class CompletedJobItemAdmin(AdminModel):
    pass


@admin.register(Client)
class ClientAdmin(AdminModel):
    pass


@admin.register(StartedJob)
class StartedJobAdmin(AdminModel):
    pass
