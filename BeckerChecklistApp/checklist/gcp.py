from google.cloud.storage import Client
from django.conf import settings


storage_client = Client() if not settings.TESTING else None


def gcp_storage_sync():
    """Sync db file back to GCP"""
    if not settings.TESTING:
        db_file_name = settings.DATABASES.get("default").get("NAME")
        storage_client.bucket("bhm_app_db").blob("db.sqlite3").upload_from_filename(
            db_file_name
        )
