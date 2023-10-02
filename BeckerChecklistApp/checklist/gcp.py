import time
from checklist.logging import get_logger
from google.cloud.storage import Client
from django.conf import settings

LOGGER = get_logger()


try:
    storage_client = Client()
except Exception as e:
    storage_client = None


def fetch_db():
    """Pull down db file from blob storage"""
    if storage_client and not settings.TESTING:
        with settings.DB_LOCK:
            db_file_name = settings.DATABASES.get("default").get("NAME")
            storage_client.bucket("bhm_app_db").blob("db.sqlite3").download_to_filename(
                db_file_name
            )            

def gcp_storage_sync():
    """Sync db file back to GCP every 1 min"""
    if storage_client and not settings.TESTING:
        with settings.DB_LOCK:
            LOGGER.info("Syncing DB")
            db_file_name = settings.DATABASES.get("default").get("NAME")
            storage_client.bucket("bhm_app_db").blob("db.sqlite3").upload_from_filename(
                db_file_name
            )

