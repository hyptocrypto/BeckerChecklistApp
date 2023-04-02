from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Job(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"


class JobItem(BaseModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField()

    def __repr__(self):
        return f"{self.job.name}({self.name})"

    def __str__(self):
        return f"{self.job.name}({self.name})"


class CompletedJob(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    check_list_completed = models.BooleanField(default=False)

    def __repr__(self):
        return f"Completed({self.job}) - {self.user}"

    def __str__(self):
        return f"Completed({self.job}) - {self.user}"


class CompletedJobItem(BaseModel):
    completed_job = models.ForeignKey(CompletedJob, on_delete=models.CASCADE)
    job_item = models.ForeignKey(JobItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f"{self.user} {self.job_item}"

    def __str__(self):
        return f"{self.user} {self.job_item}"
