import os
import json

def ler_paginas(pasta="database"):
    textos = {}
    for arq in os.listdir(pasta):
        if arq.endswith(".txt"):
            with open(os.path.join(pasta, arq), "r", encoding="utf-8") as f:
                textos[arq] = f.read()
    return textos


def salvar_json(nome, conteudo):
    os.makedirs("results", exist_ok=True)
    with open(f"results/{nome.replace('.txt', '.json')}", "w", encoding="utf-8") as f:
        f.write(conteudo)


def salvar_resumo(dados):
    os.makedirs("results", exist_ok=True)
    with open("results/resumo_semana.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
