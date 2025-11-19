#arquivo de simulação para acesso ao watsonx usando a biblioteca ibm-watsonx-ai

import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes

# 1. Defina as credenciais
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com", # Verifique a região da sua instância
    api_key="SUA_IBM_CLOUD_API_KEY"
)

project_id = "SEU_PROJECT_ID_DO_WATSONX"

# 2. Escolha o modelo (Granite)
# Você pode listar os modelos disponíveis para pegar o ID exato se necessário
model_id = "ibm/granite-13b-chat-v2" 

# 3. Defina os parâmetros de geração (opcional, mas recomendado)
parameters = {
    GenParams.DECODING_METHOD: "greedy", # ou 'sample' para mais criatividade
    GenParams.MAX_NEW_TOKENS: 200,       # Limite da resposta
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.7,          # Criatividade (se usar sample)
    GenParams.REPETITION_PENALTY: 1.1
}

# 4. Inicialize o modelo
model = Model(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=project_id
)

# 5. Defina o prompt
prompt_text = """
Responda de forma concisa e em português.
Pergunta: O que são modelos LLM e como o Granite se diferencia?
Resposta:
"""

# 6. Gere a resposta
print("Gerando resposta com IBM Granite...")
response = model.generate_text(prompt=prompt_text)

print("-" * 30)
print(response)
print("-" * 30)