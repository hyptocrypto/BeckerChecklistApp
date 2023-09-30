from threading import Thread
from django.apps import AppConfig

from checklist.gcp import gcp_storage_sync


class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checklist"

    def ready(self):
        """On start up, start background thread to update db file periodically"""
        gcp_storage_sync
        
