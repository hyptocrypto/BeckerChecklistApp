from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Job(BaseModel):
    """The abstract definition of a job"""

    name = models.CharField(max_length=200)
    description = models.TextField()

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"


class JobItem(BaseModel):
    """The abstract definition of a job item"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField()

    def __repr__(self):
        return f"{self.job.name}({self.name})"

    def __str__(self):
        return f"{self.job.name}({self.name})"


class StartedJob(BaseModel):
    """A job started by a user that contains info about competed items"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=200, default="")

    def __repr__(self):
        return f"{self.job.name}({self.user}-{self.client_name})"

    def __str__(self):
        return f"{self.job.name}({self.user}-{self.client_name})"

    def is_complete(self):
        """Check if completed job exists for this started job"""

        return CompletedJob.objects.filter(started_job=self).exists()

    def all_items_complete(self):
        """Check if all possible CompletedJobItems exist"""

        job_items = JobItem.objects.filter(
            job=self.job
        )  # All job items for this job type
        completed_job_items = CompletedJobItem.objects.filter(started_job=self)

        return sorted(job_items) == sorted([j.job_item for j in completed_job_items])


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

    def __repr__(self):
        return f"Completed({self.job}) - {self.user}"

    def __str__(self):
        return f"Completed({self.job}) - {self.user}"
