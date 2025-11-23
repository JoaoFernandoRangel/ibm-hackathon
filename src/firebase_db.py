# filepath: src/firebase_db.py
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)


def init_firebase():
    """Initialize Firestore if the credentials file exists.

    If the credentials file is not found or initialization fails,
    this returns None and the save functions become no-ops.
    """
    cred_path = "segredos/hackaton-paulino-firebase-adminsdk-fbsvc-daecf94e45.json"

    if not os.path.exists(cred_path):
        logger.warning("Firebase credentials not found at %s — Firebase disabled.", cred_path)
        return None

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        logger.exception("Failed to initialize Firebase: %s", e)
        return None


db = init_firebase()


def save_page_result(page_name: str, data: dict):
    """Save a page JSON to Firestore (no-op if Firebase not initialized)."""
    if db is None:
        logger.info("save_page_result skipped: Firebase not configured. Page: %s", page_name)
        return

    db.collection("diary_pages").document(page_name).set(data)


def save_week_summary(data: dict):
    """Save weekly summary to Firestore (no-op if Firebase not initialized)."""
    if db is None:
        logger.info("save_week_summary skipped: Firebase not configured.")
        return

    db.collection("diary_summaries").document("latest").set(data)
