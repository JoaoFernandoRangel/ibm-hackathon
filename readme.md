// ...existing code...
# 📘 Granite Diary Analyzer — README Oficial (versão atualizada)

Ferramenta de **análise automática de páginas de diário**, usando **IBM Granite (local ou Watsonx.ai)** e **armazenamento em Firestore (Firebase)**.

Ideal para **hackathons**, **POCs** e **demonstrações rápidas de NLP**, com pipeline simples, modular e fácil de testar.

---

## Estrutura do projeto (atual)

```
database/
results/
segredos/
src/
    __init__.py
    Diary.py
    firebase_db.py
app.py
main.py      ← (novo, criado conforme você pediu)
readme.md
req.txt
test_firebase.py
```

---

## 🚀 Funcionalidades

### 🔍 Extração automática
Ao processar cada página, o sistema retorna:
- Quantidade de menções de **tristeza**
- Lista de **pessoas mencionadas**
- Lista de **interações relevantes**
- Lista de **sentimentos presentes**
- JSON limpo e validado

### 💾 Armazenamento integrado
- **Firestore (Firebase)** com funções para:
  - salvar resultado
  - carregar documento
  - consultar coleções
  - buscar por campo

### 🧠 Dois modos de execução
- **Local** (Transformers + GPU)
- **Watsonx.ai** (API Granite)

### 🧱 Arquitetura simples
Focada em permitir leitura fácil durante o hackathon.

---

## 📂 Estrutura atual do projeto (descrição)
```
project/
│
├── database/          # Arquivos .txt para analisar
├── results/           # Resultados JSON salvos localmente
├── segredos/          # firebase_key.json (não comitar)
│
├── src/
│   ├── Diary.py       # Objeto principal — Granite + Watsonx + Firestore
│   ├── firebase_db.py # Wrap do Firestore (salvar, ler, consultar)
│   └── __init__.py
│
├── app.py             # Interface Streamlit (opcional)
├── main.py            # NOVO: tutorial prático de uso para seu amigo
├── test_firebase.py   # Testes isolados do Firestore
├── req.txt            # Dependências
└── readme.md          # Este arquivo
```

---

## 🛠️ Instalação

No terminal (dentro do projeto):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt
```

Certifique-se de colocar sua chave:
```
segredos/firebase_key.json
```

---

## 🔧 Configurando o Firebase

No `src/firebase_db.py` inclua algo como:
```python
from firebase_admin import credentials, initialize_app
cred = credentials.Certificate("segredos/firebase_key.json")
initialize_app(cred)
```

A **coleção padrão** usada é:
```
diary_results
```

---

## 🧩 Como o objeto Diary funciona

O arquivo `src/Diary.py` contém a classe principal `DiaryAnalyzer`, com:
- backend: `"local"` ou `"watsonx"`
- integração com Firestore
- métodos:
  - `load_model()` — carrega backend local ou Watsonx
  - `extract(text)` — chama Granite para extrair informações
  - `save_json(name, content)` — salva localmente
  - `run_single_page(text, page_name)` — processa 1 página e salva no Firestore
  - `run()` — processa toda a pasta `database/` e gera resumo semanal
  - `get_document(collection, document_id)` — busca documento no Firestore
  - `query_collection(collection, field, op, value)` — consulta com filtro
  - `list_all(collection)` — lista todos os documentos de uma coleção

---

## ▶️ Como rodar análises localmente

Processar apenas 1 página:
```bash
python3 main.py --page pagina1.txt
```

Processar tudo:
```bash
python3 main.py --all
```

Usar Watsonx.ai:
```bash
python3 main.py --backend watsonx
```

(Se preferir, use também o CLI em test_firebase.py ou uma UI Streamlit se existir.)

---

## 🆕 main.py — Arquivo de demonstração

O `main.py` proposto mostra como:
- processar 1 página
- processar todas as páginas
- salvar resultados no Firebase
- consultar e listar documentos

(Quer que eu gere esse `main.py` de exemplo agora?)

---

## 🧪 Testando Firebase separadamente

Executar:
```bash
python3 test_firebase.py
```
Inclui:
- salvar página
- ler documento
- consultar coleção

---

## 📦 Formato de saída

Exemplo de JSON gerado:
```json
{
  "tristeza": 2,
  "pessoas_mencionadas": ["Ana", "João"],
  "interacoes": ["Conversa com João"],
  "sentimentos": ["tristeza", "saudade"]
}
```

Resumo semanal (exemplo):
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

## 🧑‍💻 Fluxo geral de uso

1. Colocar `.txt` em `database/`
2. Rodar `main.py` (ou executar fluxo via Streamlit)
3. JSON aparece em `results/`
4. Também enviado ao Firestore
5. Pode consultar via:
   - Firebase Console
   - `test_firebase.py`
   - métodos em `src/firebase_db.py`

---

## ✔️ Pronto para hackathons!
- modular
- simples
- fácil de ensinar
- backend alternável
- Firestore plugado
- app Streamlit incluído

Se quiser, posso:
- gerar `main.py` de exemplo agora,
- criar `src/firebase_db.py` se faltar,
- ou produzir um diagrama/fluxograma.
```// filepath: /hackaton/readme.md
// ...existing code...
# 📘 Granite Diary Analyzer — README Oficial (versão atualizada)

Ferramenta de **análise automática de páginas de diário**, usando **IBM Granite (local ou Watsonx.ai)** e **armazenamento em Firestore (Firebase)**.

Ideal para **hackathons**, **POCs** e **demonstrações rápidas de NLP**, com pipeline simples, modular e fácil de testar.

---

## Estrutura do projeto (atual)

```
database/
results/
segredos/
src/
    __init__.py
    Diary.py
    firebase_db.py
app.py
main.py      ← (novo, criado conforme você pediu)
readme.md
req.txt
test_firebase.py
```

---

## 🚀 Funcionalidades

### 🔍 Extração automática
Ao processar cada página, o sistema retorna:
- Quantidade de menções de **tristeza**
- Lista de **pessoas mencionadas**
- Lista de **interações relevantes**
- Lista de **sentimentos presentes**
- JSON limpo e validado

### 💾 Armazenamento integrado
- **Firestore (Firebase)** com funções para:
  - salvar resultado
  - carregar documento
  - consultar coleções
  - buscar por campo

### 🧠 Dois modos de execução
- **Local** (Transformers + GPU)
- **Watsonx.ai** (API Granite)

### 🧱 Arquitetura simples
Focada em permitir leitura fácil durante o hackathon.

---

## 📂 Estrutura atual do projeto (descrição)
```
project/
│
├── database/          # Arquivos .txt para analisar
├── results/           # Resultados JSON salvos localmente
├── segredos/          # firebase_key.json (não comitar)
│
├── src/
│   ├── Diary.py       # Objeto principal — Granite + Watsonx + Firestore
│   ├── firebase_db.py # Wrap do Firestore (salvar, ler, consultar)
│   └── __init__.py
│
├── app.py             # Interface Streamlit (opcional)
├── main.py            # NOVO: tutorial prático de uso para seu amigo
├── test_firebase.py   # Testes isolados do Firestore
├── req.txt            # Dependências
└── readme.md          # Este arquivo
```

---

## 🛠️ Instalação

No terminal (dentro do projeto):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt
```

Certifique-se de colocar sua chave:
```
segredos/firebase_key.json
```

---

## 🔧 Configurando o Firebase

No `src/firebase_db.py` inclua algo como:
```python
from firebase_admin import credentials, initialize_app
cred = credentials.Certificate("segredos/firebase_key.json")
initialize_app(cred)
```

A **coleção padrão** usada é:
```
diary_results
```

---

## 🧩 Como o objeto Diary funciona

O arquivo `src/Diary.py` contém a classe principal `DiaryAnalyzer`, com:
- backend: `"local"` ou `"watsonx"`
- integração com Firestore
- métodos:
  - `load_model()` — carrega backend local ou Watsonx
  - `extract(text)` — chama Granite para extrair informações
  - `save_json(name, content)` — salva localmente
  - `run_single_page(text, page_name)` — processa 1 página e salva no Firestore
  - `run()` — processa toda a pasta `database/` e gera resumo semanal
  - `get_document(collection, document_id)` — busca documento no Firestore
  - `query_collection(collection, field, op, value)` — consulta com filtro
  - `list_all(collection)` — lista todos os documentos de uma coleção

---

## ▶️ Como rodar análises localmente

Processar apenas 1 página:
```bash
python3 main.py --page pagina1.txt
```

Processar tudo:
```bash
python3 main.py --all
```

Usar Watsonx.ai:
```bash
python3 main.py --backend watsonx
```

(Se preferir, use também o CLI em test_firebase.py ou uma UI Streamlit se existir.)

---

## 🆕 main.py — Arquivo de demonstração

O `main.py` proposto mostra como:
- processar 1 página
- processar todas as páginas
- salvar resultados no Firebase
- consultar e listar documentos

(Quer que eu gere esse `main.py` de exemplo agora?)

---

## 🧪 Testando Firebase separadamente

Executar:
```bash
python3 test_firebase.py
```
Inclui:
- salvar página
- ler documento
- consultar coleção

---

## 📦 Formato de saída

Exemplo de JSON gerado:
```json
{
  "tristeza": 2,
  "pessoas_mencionadas": ["Ana", "João"],
  "interacoes": ["Conversa com João"],
  "sentimentos": ["tristeza", "saudade"]
}
```

Resumo semanal (exemplo):
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

## 🧑‍💻 Fluxo geral de uso

1. Colocar `.txt` em `database/`
2. Rodar `main.py` (ou executar fluxo via Streamlit)
3. JSON aparece em `results/`
4. Também enviado ao Firestore
5. Pode consultar via:
   - Firebase Console
   - `test_firebase.py`
   - métodos em `src/firebase_db.py`

---

## ✔️ Pronto para hackathons!
- modular
- simples
- fácil de ensinar
- backend alternável
- Firestore plugado
- app Streamlit incluído

Se quiser, posso:
- gerar `main.py` de exemplo agora,
- criar `src/firebase_db.py` se faltar,
- ou produzir um diagrama/fluxograma.