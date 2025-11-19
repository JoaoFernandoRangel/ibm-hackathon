def montar_prompt(texto):
    return f"""
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


def limpar_json(texto):
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio != -1 and fim != -1:
        return texto[inicio:fim+1]
    return texto
