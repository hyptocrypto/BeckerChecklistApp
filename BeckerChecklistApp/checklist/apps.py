from django.conf import settings
from google.cloud.storage import Client
from django.apps import AppConfig


class ChecklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checklist"

    def ready(self):
        """On start up, pull down the db file from google cloud storage"""

        db_file_name = settings.DATABASES.get("default").get("NAME")
        Client().bucket("bhm_app_db").blob("db.sqlite3").download_to_filename(
            db_file_name
        )
