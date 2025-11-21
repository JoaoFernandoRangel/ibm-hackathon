from transformers import AutoTokenizer, AutoModelForCausalLM
from .config import MODEL_NAME, MODEL_CONFIG

def load_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_NAME)

def load_model():
    return AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        **MODEL_CONFIG
    )
