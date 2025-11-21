# Credenciais e configurações do Watsonx

WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
WATSONX_API_KEY = "SUA_IBM_CLOUD_API_KEY"
WATSONX_PROJECT_ID = "SEU_PROJECT_ID_DO_WATSONX"

WATSONX_MODEL_ID = "ibm/granite-13b-chat-v2"

GEN_PARAMS = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "min_new_tokens": 1,
    "temperature": 0.7,
    "repetition_penalty": 1.1
}
