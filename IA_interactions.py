

# --------------------------------------------------------------
# 🔮 FUTURE AI INTEGRATION PLACEHOLDER 
# --------------------------------------------------------------
def process_text_with_ai(raw_text: str) -> dict:
    """
    Esta função é apenas um placeholder!
    No futuro, você irá integrar sua IA aqui.

    Ela deve:
    - Receber o texto original do arquivo
    - Retornar um dicionário preenchido com os campos do JSON

    Por enquanto, só retorna o symptoms_description.
    """

    if not raw_text:
        return {}

    return {
        "symptoms_description": raw_text
    }


def process_pdf_with_ai(pdf_bytes: bytes, filename: str) -> dict:
    """
    Placeholder para a IA que vai extrair dados relevantes dos exames.

    No futuro, substitua este conteúdo por:
       - chamada para OpenAI
       - WatsonX
       - LLaMA
       - pipeline pessoal, etc.

    A função deve SEMPRE retornar um dicionário (JSON).
    """

    # EXEMPLO FICTÍCIO — apenas para demonstrar a estrutura
    return {
        "exam_name": filename,
        "status": "processed",
        "values": {
            "Hemoglobin": "13.4 g/dL",
            "Leukocytes": "6,800 /mm³",
            "Glucose": "92 mg/dL"
        }
    }