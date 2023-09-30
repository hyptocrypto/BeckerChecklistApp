from django.conf import settings
from django.apps import AppConfig

from checklist.gcp import gcp_storage_sync()

class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checklist"

    def ready(self):
        """On start up, pull down the db file from google cloud storage"""
        gcp_storage_sync()
