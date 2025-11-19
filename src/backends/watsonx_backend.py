from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model
from src.config_watsonx import (
    WATSONX_URL, WATSONX_API_KEY, WATSONX_PROJECT_ID,
    WATSONX_MODEL_ID, GEN_PARAMS
)
from src.nlp import limpar_json

_model = None

def load():
    global _model
    if _model is None:
        creds = Credentials(url=WATSONX_URL, api_key=WATSONX_API_KEY)
        _model = Model(
            model_id=WATSONX_MODEL_ID,
            params=GEN_PARAMS,
            credentials=creds,
            project_id=WATSONX_PROJECT_ID
        )
    return _model


def infer(texto_prompt):
    model = load()
    response = model.generate_text(prompt=texto_prompt)
    return limpar_json(response)
