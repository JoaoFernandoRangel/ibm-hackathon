# filepath: src/firebase_db.py

import firebase_admin
from firebase_admin import credentials, firestore


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("segredos/hackaton-paulino-firebase-adminsdk-fbsvc-daecf94e45.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = init_firebase()


def save_page_result(page_name: str, data: dict):
    """
    Salva o JSON de uma página no Firestore.
    Coleção: diary_pages
    Documento: page_name
    """
    db.collection("diary_pages").document(page_name).set(data)


def save_week_summary(data: dict):
    """
    Salva resumo semanal.
    Coleção: diary_summaries
    Documento: latest
    """
    db.collection("diary_summaries").document("latest").set(data)
