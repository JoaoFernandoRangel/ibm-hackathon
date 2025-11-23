# filepath: src/cloudant_db.py

from cloudant.client import CouchDB, Cloudant
from cloudant.error import CloudantException
import json
import os


class CloudantDB:
    """NoSQL backend to save and query results using IBM Cloudant."""

    def __init__(
        self,
        username: str,
        api_key: str,
        url: str,
        db_name: str = "diary_data",
        create_if_missing: bool = True
    ):
        """
        Initialize connection to Cloudant.
        - username: Cloudant username
        - api_key: API key or password
        - url: Cloudant URL (e.g. https://<id>.cloudantnosqldb.appdomain.cloud )
        - db_name: database name
        """

        self.username = username
        self.api_key = api_key
        self.url = url
        self.db_name = db_name

        try:
            # Autenticação padrão (API Key)
            self.client = Cloudant(self.username, self.api_key, url=self.url, connect=True)

                if create_if_missing and db_name not in self.client.all_dbs():
                    print(f"[🗄️] Creating database '{db_name}'...")
                    self.client.create_database(db_name)

            self.db = self.client[db_name]

            print("[☁️] Cloudant connected successfully.")

        except CloudantException as e:
            print("[ERROR] Failed to connect to Cloudant")
            raise e

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------

    def save(self, doc_id: str, data: dict):
        """Salva ou atualiza um documento com ID fixo."""
        try:
            doc = self.db.get(doc_id)
            if doc:
                print(f"[♻️] Updating document: {doc_id}")
                doc.update(data)
                doc.save()
            else:
                print(f"[💾] Creating new document: {doc_id}")
                self.db.create_document({ "_id": doc_id, **data })

        except Exception as e:
            print(f"[ERROR] Could not save '{doc_id}': {e}")

    def get(self, doc_id: str):
        """Recupera um documento pelo ID."""
        try:
            doc = self.db.get(doc_id)
            if doc:
                return dict(doc)
            return None
        except Exception as e:
            print(f"[ERROR] Could not retrieve '{doc_id}': {e}")
            return None

    def delete(self, doc_id: str):
        """Remove um documento."""
        try:
            doc = self.db.get(doc_id)
            if doc:
                doc.delete()
                print(f"[🗑️] Document '{doc_id}' removed.")
        except Exception as e:
            print(f"[ERROR] Could not delete '{doc_id}': {e}")

    def list_all(self):
        """Lista todos os documentos do DB."""
        try:
            return [dict(self.db[d]) for d in self.db]
        except Exception as e:
            print(f"[ERROR] Failed to list documents: {e}")
            return []

    # ---------------------------------------------------------
    # Queries estilo Mango
    # ---------------------------------------------------------
    def query(self, field: str, value):
        """
        Consulta documentos onde field == value usando Mango Query.
        """
        selector = { field: { "$eq": value } }
        try:
            result = self.db.get_query_result(selector)
            return [r for r in result]
        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            return []


from cloudant.client import Cloudant

# Cloudant configuration (example placeholders)
username = "your_username"
api_key = "your_api_key"
url = "https://your_url.cloudant.com"

# Cria uma instância do cliente Cloudant
client = Cloudant(username, api_key, url=url)

# Functions to replace Firebase usage with Cloudant
def save_page_result(page_name, data):
    db = client["diary_data"]
    doc = db.get(page_name)
    if doc:
        doc.update(data)
        doc.save()
    else:
        db.create_document({ "_id": page_name, **data })

def save_week_summary(summary):
    db = client["diary_data"]
    doc = db.get("resumo_semana")
    if doc:
        doc.update(summary)
        doc.save()
    else:
        db.create_document({ "_id": "resumo_semana", **summary })