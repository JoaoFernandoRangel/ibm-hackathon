import streamlit as st
from testes import  salvar_json, extrair_json, ler_paginas, limpar_json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

model_name = "ibm-granite/granite-3.0-2b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="cuda",
    dtype=torch.float16
)


paginas = ler_paginas("database")

dados_agrupados = {
    "total_tristeza": 0,
    "todas_pessoas": set(),
    "todas_interacoes": [],
}

for nome, texto in paginas.items():
    print("Processando:", nome)

    resposta_json = extrair_json(texto)
    salvar_json(nome, resposta_json)

    dados = json.loads(resposta_json)

    dados_agrupados["total_tristeza"] += dados.get("tristeza", 0)
    dados_agrupados["todas_pessoas"].update(dados.get("pessoas_mencionadas", []))
    dados_agrupados["todas_interacoes"].extend(dados.get("interacoes", []))


# Finalizar
dados_agrupados["todas_pessoas"] = list(dados_agrupados["todas_pessoas"])

with open("results/resumo_semana.json", "w", encoding="utf-8") as f:
    json.dump(dados_agrupados, f, indent=4, ensure_ascii=False)

print("\n✓ Processamento concluído! JSONs salvos em: results/")
st.title("Isso é uma página de streamlit")
if st.button("Botão"):
    print("--")
    f.func()