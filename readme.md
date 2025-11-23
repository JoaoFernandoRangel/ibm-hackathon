# 📘 xTeF Clinic

## Testing granite and text analysis.

Tool for **automatic analysis of diary pages**, using **IBM Granite (local or Watsonx.ai)** and **Firestore (Firebase)** for storage.

Ideal for **hackathons**, **POCs**, and **quick NLP demonstrations**, with a simple, modular, and easy-to-test pipeline.


## 📂 Project Structure

````
database/
results/
secrets/
src/
**init**.py
Diary.py
firebase_db.py
app.py
main.py
readme.md
req.txt
test_firebase.py
````

## 🚀 Features

### 🔍 Automatic Extraction

For each processed page, the system extracts:

- Number of **sadness** mentions  
- List of **people mentioned**  
- List of **relevant interactions**  
- List of **emotions present**  
- Clean and validated JSON output  

### 💾 Integrated Storage

Using **Firestore (Firebase)**:

- Save results  
- Load documents  
- Query collections  
- Filter by field  

### 🧠 Two Execution Modes

- **Local** (Transformers + GPU)  
- **Watsonx.ai** (Granite API)

### 🧱 Simple Architecture

Focused on clarity and speed for hackathons and demos.

## 🛠️ Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt
````

Place your Firebase credentials at:

```
secrets/firebase_key.json
```

## 🔧 Firebase Setup

In `src/firebase_db.py`, initialize Firestore:

```python
from firebase_admin import credentials, initialize_app
cred = credentials.Certificate("secrets/firebase_key.json")
initialize_app(cred)
```

Default collection:

```
diary_results
```

## 🧩 DiaryAnalyzer Overview

The main class lives in `src/Diary.py` and provides:

* `load_model()` — loads Granite (local or Watsonx)
* `extract(text)` — extracts structured data
* `save_json(name, content)` — saves JSON locally
* `run_single_page(text, page_name)` — processes one page + stores in Firestore
* `run()` — processes all pages in `database/`
* `get_document(collection, id)` — fetches a document
* `query_collection(collection, field, op, value)` — filtered query
* `list_all(collection)` — lists an entire collection


## ▶️ Running the Analyzer

### Process one page:

```bash
python3 main.py --page page1.txt
```

### Process all pages:

```bash
python3 main.py --all
```

### Use Watsonx.ai backend:

```bash
python3 main.py --backend watsonx
```

## 🆕 `main.py` — Demonstration Script

The included `main.py` shows:

* How to process one or multiple pages
* How to store results in Firestore
* How to query saved documents
* How to list all entries


## 🧪 Testing Firestore

Run isolated tests:

```bash
python3 test_firebase.py
```

Covers:

* Save
* Load
* Query


## 📦 Output Examples

### Page result:

```json
{
  "sadness": 2,
  "people_mentioned": ["Ana", "João"],
  "interactions": ["Conversation with João"],
  "emotions": ["sadness", "longing"]
}
```

### Weekly summary:

```json
{
  "total_sadness": 5,
  "all_people": ["Ana", "João", "Marcos"],
  "all_interactions": [
    "Conversation with João",
    "Argument with Marcos"
  ]
}
```


## 🧑‍💻 Usage Workflow

1. Add `.txt` files to `database/`
2. Run `main.py` (or Streamlit UI if using app.py)
3. JSON outputs appear in `results/`
4. Firestore automatically stores the processed data
5. Query using:

   * Firebase Console
   * `test_firebase.py`
   * Methods in `firebase_db.py`


## ✔️ Ready for Hackathons

* Modular
* Easy to understand
* Flexible (local or cloud Granite)
* Integrated database
* Perfect for demos and prototypes
