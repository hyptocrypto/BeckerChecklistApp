from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    info = models.TextField(null=True, blank=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Job(BaseModel):
    """The abstract definition of a job"""

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500)

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"


class JobItem(BaseModel):
    """The abstract definition of a job item"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __repr__(self):
        return f"{self.job.name}({self.name})"

    def __str__(self):
        return f"{self.job.name}({self.name})"


class StartedJob(BaseModel):
    """A job started by a user that contains info about competed items"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    notes = models.TextField(max_length=1000, null=True, blank=True)

    def __repr__(self):
        return f"{self.job.name}({self.user}-{self.client})"

    def __str__(self):
        return f"{self.job.name}({self.user}-{self.client})"

    def is_complete(self):
        """Check if completed job exists for this started job"""

        return CompletedJob.objects.filter(started_job=self).exists()

    def all_items_complete(self):
        """Check if all possible CompletedJobItems exist"""

        job_items = JobItem.objects.values_list("pk", flat=True).filter(job=self.job)
        completed_job_items = CompletedJobItem.objects.values_list(
            "job_item_id", flat=True
        ).filter(started_job=self)
        return sorted(job_items) == sorted(completed_job_items)


class CompletedJobItem(BaseModel):
    """Items that have been completed for a started job"""

    started_job = models.ForeignKey(StartedJob, on_delete=models.CASCADE)
    job_item = models.ForeignKey(JobItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f"{self.user} {self.job_item}"

    def __str__(self):
        return f"{self.user} {self.job_item}"


class CompletedJob(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_job = models.ForeignKey(StartedJob, on_delete=models.CASCADE)
    check_list_completed = models.BooleanField(default=False)

    def __repr__(self):
        return f"Completed({self.started_job}) - {self.user}"

    def __str__(self):
        return f"Completed({self.started_job}) - {self.user}"
