import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.config_local import MODEL_LOCAL_NAME, LOCAL_MODEL_CONFIG
from src.nlp import limpar_json

# O modelo é carregado uma vez só
_tokenizer = None
_model = None

def load():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_LOCAL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_LOCAL_NAME,
            **LOCAL_MODEL_CONFIG
        )
    return _tokenizer, _model


def infer(texto_prompt):
    tokenizer, model = load()

    inputs = tokenizer(
        texto_prompt,
        return_tensors="pt",
        truncation=True
    )
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    output = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False
    )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return limpar_json(text)
