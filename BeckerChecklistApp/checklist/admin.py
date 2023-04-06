from django.contrib import admin
from .models import Job, JobItem, CompletedJob


class JobItemInline(admin.StackedInline):
    model = JobItem
    fk_name = "job"  # specify the foreign key field name for the relationship
    extra = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = [JobItemInline]


@admin.register(JobItem)
class JobItemAdmin(admin.ModelAdmin):
    pass


@admin.register(CompletedJob)
class CompletedJobItemAdmin(admin.ModelAdmin):
    pass
