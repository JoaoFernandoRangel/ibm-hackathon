import json
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model

import KeyChain
project_id = "cf0f0ec9-62ec-4191-92e0-0c07d15a5fb0"
# ================================
# Loading API key via KeyChain
# ================================

kc = KeyChain()                   # já carrega o .env automaticamente
keys = kc.load_from_streamlit()         # ou kc.load_from_streamlit(st)

API_KEY = keys["GMAIL_APIKEY"]    # mesma apikey que estava no apikey.json
URL = "https://us-south.ml.cloud.ibm.com"

credentials = Credentials(
    api_key=API_KEY,
    url=URL
)

# ====================================
# Configuring Granite model
# ====================================

model = Model(
    model_id="ibm/granite-3-8b-instruct",
    credentials=credentials,
    params={
        "temperature": 0.2,
        "max_tokens": 600
    },
    project_id=project_id,
)


# ======================================
# Function to summarize a clinical case
# ======================================
def summarize_clinical_case(text: str) -> str:
    prompt = f"""
    You are a specialist physician. Provide an objective clinical summary of the text below:

    Text:
    {text}

    Answer in bullet points including:
    - Main symptoms
    - Relevant medical history
    - Possible differential diagnoses
    - Severity assessment
    - Red flag signs
    - Recommended immediate management
    """

    response = model.generate(prompt=prompt)
    return response["results"][0]["generated_text"]
