from threading import Thread
from django.apps import AppConfig

from checklist.gcp import fetch_db


class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checklist"

    def ready(self):
        """On start up, start background thread to update db file periodically"""
        fetch_db()
        
