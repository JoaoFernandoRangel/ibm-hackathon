# como eu não tenho acesso ao Watson, vou usar o granite por meio da biblioteca transformers
import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def ler_paginas(pasta="database"):
    textos = {}
    for arq in os.listdir(pasta):
        if arq.endswith(".txt"):
            with open(os.path.join(pasta, arq), "r", encoding="utf-8") as f:
                textos[arq] = f.read()
    return textos

def limpar_json(texto):
    # mantém só o que está entre { ... }
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio != -1 and fim != -1:
        return texto[inicio:fim+1]
    return texto

def extrair_json(texto):
    prompt = f"""
    Você receberá uma página de diário fictícia.
    Extraia em JSON estruturado as seguintes informações:

    - "tristeza": quantas vezes a pessoa demonstrou estar triste na página
    - "pessoas_mencionadas": lista de nomes mencionados
    - "interacoes": lista textual das interações importantes
    - "sentimentos": sentimentos detectados (lista)

    Texto da página:
    \"\"\"{texto}\"\"\"

    Responda **somente** com JSON válido.
    """

    # Tokenização completa (gera attention_mask)
    
    inputs = tokenizer(
    prompt,
    return_tensors="pt",
    padding=False,   # mais rápido (menos tokens)
    truncation=True
    )

    inputs = {k: v.to("cuda") for k, v in inputs.items()}


    output = model.generate(
    **inputs,
    max_new_tokens=160,  # reduzir tokens é o maior ganho de velocidade
    do_sample=False,     # deterministic = mais rápido
    num_beams=1,         # beam search deixa lento
    pad_token_id=tokenizer.eos_token_id
    )


    resposta = tokenizer.decode(output[0], skip_special_tokens=True)
    resposta = limpar_json(resposta)

    print(resposta)
    return resposta

def salvar_json(nome_arquivo, conteudo):
    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", nome_arquivo.replace(".txt", ".json")),
              "w", encoding="utf-8") as f:
        f.write(conteudo)




def main():

    
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



if __name__ == "__main__":

    main()