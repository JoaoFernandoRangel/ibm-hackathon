import json
from src.io_utils import ler_paginas, salvar_json, salvar_resumo
from src.nlp import montar_prompt

# escolha do backend: "local" ou "watsonx"
BACKEND = "local"   # altere para "watsonx" quando estiver no hackathon

if BACKEND == "local":
    from src.backends.local_backend import infer
else:
    from src.backends.watsonx_backend import infer


def main():
    paginas = ler_paginas("database")

    dados_agrupados = {
        "total_tristeza": 0,
        "todas_pessoas": set(),
        "todas_interacoes": []
    }

    for nome, texto in paginas.items():
        print("Processando:", nome)

        prompt = montar_prompt(texto)

        resposta = infer(prompt)
        salvar_json(nome, resposta)

        dados = json.loads(resposta)

        dados_agrupados["total_tristeza"] += dados.get("tristeza", 0)
        dados_agrupados["todas_pessoas"].update(dados.get("pessoas_mencionadas", []))
        dados_agrupados["todas_interacoes"].extend(dados.get("interacoes", []))

    dados_agrupados["todas_pessoas"] = list(dados_agrupados["todas_pessoas"])
    salvar_resumo(dados_agrupados)

    print("\n✓ Processamento concluído!")


if __name__ == "__main__":
    main()
