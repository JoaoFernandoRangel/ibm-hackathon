
# Granite Diary Analyzer

**Extração automática de sentimentos, pessoas e eventos a partir de páginas de diário usando IBM Granite + Transformers**

Ferramenta modular, com suporte a execução local em GPU ou via Watsonx.ai, que processa páginas de diário (.txt) e gera JSONs por página e um resumo semanal consolidado — ideal para POCs, hackathons e pipelines de NLP.

---

## Visão geral
- Extração de:
  - Quantidade de menções de tristeza
  - Pessoas mencionadas
  - Interações relevantes
  - Sentimentos expressos
- Dois backends configuráveis em tempo de execução:
  - 🖥️ BACKEND LOCAL — HuggingFace Transformers + GPU (bitsandbytes / 4‑bit)
  - ☁️ BACKEND WATSONX — chamada de API Watsonx.ai
- Outputs JSON em `results/`.

---

## Arquitetura do projeto

```
ibm-hackathon/  
│
├── src/
│   ├── backends/
│   │   ├── local_backend.py        → executa Granite localmente via Transformers/GPU
│   │   └── watsonx_backend.py      → executa Granite via Watsonx.ai
│   │
│   ├── nlp.py                      → prompt & limpeza/validação do JSON
│   ├── io_utils.py                 → leitura/escrita de arquivos
│   ├── config_local.py             → configs do modelo local
│   └── config_watsonx.py           → configs/credenciais do Watsonx
│
├── main.py                         → pipeline unificado (escolhe backend)
├── req.txt
├── database/                        → .txt input
└── results/                         → .json outputs
```

---

## Requisitos
- Debian GNU/Linux 12 (bookworm)
- Python 3.10+
- GPU Nvidia + CUDA (recomendado ≥8 GB VRAM) para backend local
- pip

Dependências principais (veja `requirements.txt` / `req.txt`): streamlit, transformers, accelerate, torch, ibm-watsonx-ai, bitsandbytes, xformers, tokenizers, sentencepiece, safetensors, orjson, pyyaml, protobuf.

---

## Instalação
No terminal (dentro do projeto):
```bash
git clone <repo-url> hackaton
cd hackaton

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt || pip install -r req.txt
```

Observação: bitsandbytes/xformers podem requerer instalação específica ao driver/CUDA.

---

## Credenciais Watsonx (opcional)
Se usar o backend Watsonx, edite:
```python
# filepath: src/config_watsonx.py
WATSONX_API_KEY = "SUA_API_KEY"
WATSONX_PROJECT_ID = "SEU_PROJECT_ID"
WATSONX_REGION = "REGIÃO"  # se aplicável
```

---

## Como escolher o backend
Edite `main.py` ou defina variável no topo do arquivo:

```python
# Em main.py
BACKEND = "local"    # ou "watsonx"
```

Nenhuma outra alteração é necessária — o pipeline usa a impl. do backend selecionado.

---

## Como rodar
1. Coloque arquivos `.txt` em `database/` (um arquivo = uma página).
2. Executar:
```bash
python3 main.py
```
3. Ou rodar UI (se existir):
```bash
streamlit run app.py
```

Resultados:
```
results/
  pagina1.json
  pagina2.json
  resumo_semana.json
```

---

## Exemplos

Entrada (database/pagina1.txt):
```
Hoje acordei muito triste. Senti falta da Ana.
Conversei com João e tentei melhorar um pouco.
Me senti triste novamente no fim do dia.
```

Saída (results/pagina1.json):
```json
{
  "tristeza": 2,
  "pessoas_mencionadas": ["Ana", "João"],
  "interacoes": ["Conversa com João"],
  "sentimentos": ["tristeza", "saudade"]
}
```

Resumo final (results/resumo_semana.json):
```json
{
  "total_tristeza": 5,
  "todas_pessoas": ["Ana", "João", "Marcos"],
  "todas_interacoes": [
    "Conversa com João",
    "Discussão com Marcos"
  ]
}
```

---

## Configurações do modelo (exemplo)
Local (src/config_local.py):
```python
MODEL_NAME = "ibm-granite/granite-3.0-2b-instruct"
MODEL_CONFIG = {
    "load_in_4bit": True,
    "torch_dtype": "float16",
    "device_map": "auto"
}
```

Watsonx (src/config_watsonx.py):
```python
WATSONX_API_KEY = "<sua_api_key>"
WATSONX_PROJECT_ID = "<seu_project_id>"
```

