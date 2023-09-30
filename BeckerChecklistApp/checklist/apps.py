from threading import Thread
from django.apps import AppConfig

from checklist.gcp import gcp_storage_sync


class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checklist"

    def ready(self):
        """On start up, pull down the db file from google cloud storage"""
        sync_daemon = Thread(target=gcp_storage_sync, daemon=True)
        sync_daemon.start()
