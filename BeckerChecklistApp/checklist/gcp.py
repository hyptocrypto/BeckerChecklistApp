from google.cloud.storage import Client
from django.conf import settings
import logging

try:
    storage_client = Client()
except Exception as e:
    storage_client = None


def gcp_storage_sync():
    """Sync db file back to GCP"""
    if not settings.TESTING:
        logging.info("Syncing DB")
        db_file_name = settings.DATABASES.get("default").get("NAME")
        storage_client.bucket("bhm_app_db").blob("db.sqlite3").upload_from_filename(
            db_file_name
        )
