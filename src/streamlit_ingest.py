# filepath: src/streamlit_ingest.py

from src.main import run_single_page   # você já tem essa função no pipeline
from src.firebase_db import save_page_result

def process_page_input(text: str, page_name: str, backend="watsonx"):
    """
    Recebe texto cru vindo do Streamlit, roda Granite e salva no Firebase.
    """

    # 1. Processa a página com Granite (local ou Watsonx)
    result_json = run_single_page(text, backend=backend)
    # result_json = {
    #   "tristeza": 2,
    #   "pessoas_mencionadas": [...],
    #   ...
    # }

    # 2. Salva no Firestore
    save_page_result(page_name, result_json)

    return result_json
