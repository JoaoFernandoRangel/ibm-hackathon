# filepath: src/firebase_db.py
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# use KeyChain to load secrets safely
from KeyChain import KeyChain

logger = logging.getLogger(__name__)


def init_firebase():
    """Initialize Firestore using credentials from KeyChain (preferred) or fallback to file.
    Returns firestore client or None.
    """
    kc = KeyChain()
    # try streamlit secrets if available, KeyChain handles missing streamlit safely
    try:
        import streamlit as st  # type: ignore
    except Exception:
        st = None
    secrets = kc.load_from_streamlit(st) if st is not None else {}
    env = kc.load_from_env() or {}

    # prefer explicit service-account fields from secrets/env
    project_id = secrets.get("FIREBASE_PROJECT_ID")

    
    private_key = secrets.get("FIREBASE_PRIVATE_KEY")
        
    
    client_email = secrets.get("FIREBASE_CLIENT_EMAIL")
        
    
    private_key_id = secrets.get("SERVICE_ACCOUNT_PRIVATE_KEY_ID")
    

    # normalize private_key if it was stored with escaped newlines
    if isinstance(private_key, str):
        private_key = private_key.strip()
        private_key = private_key.replace("\\n", "\n").strip('“”"')

    # If we have the minimal fields, construct an in-memory service account dict
    service_account_info = None
    if project_id and private_key and client_email:
        service_account_info = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id or "",
            "private_key": private_key,
            "client_email": client_email,
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
        }

    # fallback to file in segredos/ if present
    cred_file_candidates = [
        "segredos/hackaton-paulino-firebase-adminsdk-fbsvc-daecf94e45.json",
        "segredos/hackaton-paulino-7320b0ec9b90.json",
    ]
    cred_path = None
    for p in cred_file_candidates:
        if os.path.exists(p):
            cred_path = p
            break

    if service_account_info is None and cred_path is None:
        logger.warning("Firebase credentials not found (KeyChain and segredos). Firebase disabled.")
        return None

    try:
        if not firebase_admin._apps:
            if service_account_info is not None:
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
            else:
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
