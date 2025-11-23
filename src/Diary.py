import os
import json
import torch

# Watsonx
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Local Granite
from transformers import AutoTokenizer, AutoModelForCausalLM
# Adicione essencialmente APÓS seus imports:
from src.firebase_db import save_page_result, save_week_summary
from firebase_admin import credentials, firestore, initialize_app




class DiaryAnalyzer:

    def __init__(
        self,
        backend="local",
        database_path="database",
        results_path="results",

        # Local Granite
        local_model_name="ibm-granite/granite-3.0-2b-instruct",

        # Watsonx Granite
        watsonx_model="ibm/granite-3-2-8b-instruct",
        watsonx_api_key=None,
        watsonx_project_id=None
    ):

        self.backend = backend
        self.database_path = database_path
        self.results_path = results_path

        # LOCAL
        self.local_model_name = local_model_name
        self.local_tokenizer = None
        self.local_model = None

        # WATSONX
        self.watsonx_model_name = watsonx_model
        self.watsonx_model = None
        self.watsonx_api_key = watsonx_api_key
        self.watsonx_project_id = watsonx_project_id

        # Prompt base
        self.template_prompt = """
        Você receberá uma página de diário fictícia.
        Extraia em JSON estruturado as seguintes informações:

        - "tristeza": quantas vezes a pessoa demonstrou estar triste
        - "pessoas_mencionadas": lista de nomes
        - "interacoes": lista das interações importantes
        - "sentimentos": lista de sentimentos detectados

        Texto da página:
        \"\"\"{texto}\"\"\"

        Responda SOMENTE com JSON válido.
        """

    # =====================================================
    #  CARREGAMENTO DE MODELO
    # =====================================================
    def load_model(self):
        if self.backend == "local":
            print("[🔧] Carregando modelo local Granite...")
            self.local_tokenizer = AutoTokenizer.from_pretrained(self.local_model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(
                self.local_model_name,
                load_in_4bit=True,
                device_map="cuda",
                torch_dtype=torch.float16
            )
        elif self.backend == "watsonx":
            print("[☁️] Conectando ao Watsonx.ai...")
            creds = Credentials(
                url="https://us-south.ml.cloud.ibm.com",
                api_key=self.watsonx_api_key
            )
            params = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 160,
                GenParams.REPETITION_PENALTY: 1.1,
                GenParams.TEMPERATURE: 0.7
            }
            self.watsonx_model = ModelInference(
                model_id=self.watsonx_model_name,
                params=params,
                credentials=creds,
                project_id=self.watsonx_project_id
            )
        else:
            raise ValueError("backend deve ser 'local' ou 'watsonx'")


    # =====================================================
    #  UTILITÁRIOS
    # =====================================================
    @staticmethod
    def clean_json(text):
        ini = text.find("{")
        end = text.rfind("}")
        if ini == -1 or end == -1:
            return "{}"
        return text[ini:end+1]


    def load_pages(self):
        pages = {}
        for arq in os.listdir(self.database_path):
            if arq.endswith(".txt"):
                with open(os.path.join(self.database_path, arq), "r", encoding="utf-8") as f:
                    pages[arq] = f.read()
        return pages


    def save_json(self, name, content):
        os.makedirs(self.results_path, exist_ok=True)
        path = os.path.join(self.results_path, name.replace(".txt", ".json"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


    # =====================================================
    #  GERADOR DE JSON
    # =====================================================
    def extract(self, text):

        prompt = self.template_prompt.format(texto=text)

        # -------------- LOCAL --------------
        if self.backend == "local":

            inputs = self.local_tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True
            )

            inputs = {k: v.to("cuda") for k, v in inputs.items()}

            output = self.local_model.generate(
                **inputs,
                max_new_tokens=160,
                do_sample=False,
                pad_token_id=self.local_tokenizer.eos_token_id
            )

            decoded = self.local_tokenizer.decode(output[0], skip_special_tokens=True)
            return self.clean_json(decoded)

        # -------------- WATSONX --------------
        else:

            response = self.watsonx_model.generate_text(prompt=prompt)
            return self.clean_json(response)

    def run_single_page(self, text: str, page_name: str):
        """
        Método simples para uso via Streamlit:
        
        - recebe texto cru (não precisa de .txt)
        - roda Granite (local ou watsonx)
        - converte p/ JSON
        - salva no Firebase
        - retorna dict (não string)
        """

        # Garante que o modelo está carregado
        if (self.backend == "local" and self.local_model is None) or \
           (self.backend == "watsonx" and self.watsonx_model is None):
            self.load_model()

        output_json = self.extract(text)
        data = json.loads(output_json)

        # === salvar no Firestore ===
        save_page_result(page_name, data)

        return data
    # =====================================================
    #  FIREBASE (WRITE / QUERY)
    # =====================================================

    def save_to_firestore(self, collection, document_id, data):
        """
        Salva um dicionário no Firestore.
        """
        try:
            db = firestore.client()
            db.collection(collection).document(document_id).set(data)
            print(f"[🔥] Documento salvo no Firestore: {collection}/{document_id}")
        except Exception as e:
            print(f"[ERRO FIRESTORE] {e}")


    def get_document(self, collection, document_id):
        """
        Busca um documento pelo ID.
        """
        try:
            db = firestore.client()
            doc_ref = db.collection(collection).document(document_id)
            doc = doc_ref.get()

            if doc.exists:
                print(f"[🔥] Documento encontrado: {collection}/{document_id}")
                return doc.to_dict()
            else:
                print(f"[!] Documento não existe: {collection}/{document_id}")
                return None

        except Exception as e:
            print(f"[ERRO FIRESTORE] {e}")
            return None


    def query_collection(self, collection, field, op, value):
        """
        Consulta avançada.

        op pode ser:
        - '=='
        - '<'
        - '<='
        - '>'
        - '>='
        - 'array_contains'

        EXEMPLO:
            query_collection("paginas", "tristeza", ">=", 2)
        """
        try:
            db = firestore.client()
            results = db.collection(collection).where(field, op, value).stream()

            output = [doc.to_dict() for doc in results]
            print(f"[🔥] {len(output)} resultados encontrados em '{collection}'")

            return output

        except Exception as e:
            print(f"[ERRO FIRESTORE] {e}")
            return []


    def list_all(self, collection):
        """
        Lista todos os documentos de uma coleção.
        """
        try:
            db = firestore.client()
            docs = db.collection(collection).stream()

            output = {doc.id: doc.to_dict() for doc in docs}
            print(f"[🔥] Coleção '{collection}' retornou {len(output)} docs")

            return output

        except Exception as e:
            print(f"[ERRO FIRESTORE] {e}")
            return {}

    # =====================================================
    #  PACIENTES (CRUD SIMPLES)
    # =====================================================
    def save_patient(self, form_data: dict):
        """
        Salva dados do paciente na coleção 'pacientes'.
        Usa o email como ID do documento.
        """
        try:
            email = form_data.get("email")
            if not email:
                raise ValueError("O campo 'email' é obrigatório para salvar o paciente.")
            
            db = firestore.client()
            db.collection("pacientes").document(email).set(form_data)
            print(f"[🔥] Paciente salvo: pacientes/{email}")
            return True

        except Exception as e:
            print(f"[ERRO SAVE_PATIENT] {e}")
            return False


    def get_patient(self, email: str):
        """
        Busca documento completo do paciente pelo email.
        """
        try:
            db = firestore.client()
            doc = db.collection("pacientes").document(email).get()

            if doc.exists:
                print(f"[🔥] Paciente encontrado: {email}")
                return doc.to_dict()
            else:
                print(f"[!] Paciente NÃO encontrado: {email}")
                return None

        except Exception as e:
            print(f"[ERRO GET_PATIENT] {e}")
            return None


    def query_patient_by_name(self, name: str):
        """
        Busca paciente(s) pelo nome exato.
        """
        try:
            db = firestore.client()
            docs = db.collection("pacientes").where("name", "==", name).stream()
            results = [d.to_dict() for d in docs]

            print(f"[🔥] {len(results)} pacientes encontrados com o nome '{name}'")
            return results
        except Exception as e:
            print(f"[ERRO QUERY_BY_NAME] {e}")
            return []


    def list_patients(self):
        """
        Lista todos os pacientes registrados.
        """
        try:
            db = firestore.client()
            docs = db.collection("pacientes").stream()

            output = {doc.id: doc.to_dict() for doc in docs}
            print(f"[🔥] {len(output)} pacientes encontrados no Firebase")

            return output

        except Exception as e:
            print(f"[ERRO LIST_PATIENTS] {e}")
            return {}

    # =====================================================
    #  PIPELINE PRINCIPAL
    # =====================================================
    def run(self):

        self.load_model()

        pages = self.load_pages()

        summary = {
            "total_tristeza": 0,
            "todas_pessoas": set(),
            "todas_interacoes": []
        }

        for name, text in pages.items():
            print(f"📄 Processando {name}...")

            output_json = self.extract(text)
            self.save_json(name, output_json)

            data = json.loads(output_json)

            # --- salva cada página no Firebase ---
            page_name_clean = name.replace(".txt", "")
            save_page_result(page_name_clean, data)

            summary["total_tristeza"] += data.get("tristeza", 0)
            summary["todas_pessoas"].update(data.get("pessoas_mencionadas", []))
            summary["todas_interacoes"].extend(data.get("interacoes", []))

        summary["todas_pessoas"] = list(summary["todas_pessoas"])

        # salva em disco
        with open(os.path.join(self.results_path, "resumo_semana.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)

        # --- salva resumo no Firebase ---
        save_week_summary(summary)

        print("\n✓ Processamento concluído!\nJSONs salvos em:", self.results_path)

    # =====================================================
    #  CARREGAR TODOS OS DADOS DE UM PACIENTE
    # =====================================================
    def get_all_patient_records(self, email: str) -> dict:
        """
        Retorna todos os documentos no Firebase que pertencem ao paciente:
        - pacientes/{email}
        - paginas/...
        - resumo_semana/...
        - pre_prontuario/...
        """
        try:
            db = firestore.client()
            data = {}

            # 1) Dados do paciente
            doc = db.collection("pacientes").document(email).get()
            if doc.exists:
                data["perfil"] = doc.to_dict()

            # 2) Páginas e análises individuais
            pages = db.collection("paginas").where("email", "==", email).stream()
            data["paginas"] = [p.to_dict() for p in pages]

            # 3) Resumo de semana
            summaries = db.collection("resumos_semana").where("email", "==", email).stream()
            data["resumos_semana"] = [s.to_dict() for s in summaries]

            # 4) Pre-prontuário
            pronts = db.collection("pre_prontuario").where("email", "==", email).stream()
            data["pre_prontuario"] = [p.to_dict() for p in pronts]

            return data

        except Exception as e:
            print(f"[ERRO get_all_patient_records] {e}")
            return {}
    
    def merge_patient_records_as_text(self, records: dict) -> str:
        """
        Converte todos os JSONs do paciente em um único texto estruturado
        para o Granite processar.
        """

        combined = []

        # Perfil
        if "perfil" in records:
            combined.append("=== PATIENT PROFILE ===\n")
            combined.append(json.dumps(records["perfil"], indent=2, ensure_ascii=False))

        # Diários / páginas
        for p in records.get("paginas", []):
            combined.append("\n=== PAGE ENTRY ===\n")
            combined.append(json.dumps(p, indent=2, ensure_ascii=False))

        # Pre-prontuário
        for pr in records.get("pre_prontuario", []):
            combined.append("\n=== PRE-PRONTUARIO ===\n")
            combined.append(json.dumps(pr, indent=2, ensure_ascii=False))

        # Resumo de semana
        for rs in records.get("resumos_semana", []):
            combined.append("\n=== WEEK SUMMARY ===\n")
            combined.append(json.dumps(rs, indent=2, ensure_ascii=False))

        return "\n\n".join(combined)



    # =====================================================
    # SUMARIZAÇÃO DO CASO CLÍNICO (USANDO GRANITE)
    # =====================================================
    def generate_summary_from_text(self, text: str, max_new_tokens: int = 512, tone: str | None = None, custom_prompt: str | None = None) -> str:
        """Gera um resumo clínico a partir de um texto completo usando o backend configurado.

        Retorna o texto cru do resumo (string).
        """

        # If the user provides a custom prompt, use it directly
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt + "\n\n" + text
        else:
            tone_text = f"Use tone: {tone}." if tone else ""
            prompt = f"""
You are an experienced clinical assistant. You will receive multiple notes for a patient (diaries, results, observations). Based on the content below, generate an objective and structured clinical summary in English containing:

- Brief identification (e.g., patient, age group when available)
- Chief complaint
- History of present illness (timeline and key points)
- Relevant lab/test findings
- Important findings / signs and symptoms
- Diagnostic impression (differential hypotheses)
- Brief recommendations (additional tests, referrals, immediate management)

Respond in readable text (paragraphs and bullets when appropriate). Do not respond with JSON.

{tone_text}

Content of the notes:
"""
            prompt += "\n" + text

        # Geração local
        if self.backend == "local":
            if self.local_model is None or self.local_tokenizer is None:
                self.load_model()

            inputs = self.local_tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )

            inputs = {k: v.to("cuda") for k, v in inputs.items()}

            output = self.local_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.local_tokenizer.eos_token_id
            )

            decoded = self.local_tokenizer.decode(output[0], skip_special_tokens=True)
            return decoded

        # Geração via Watsonx
        else:
            if self.watsonx_model is None:
                self.load_model()

            try:
                # Passa parâmetros para controlar tamanho da resposta
                params = {
                    GenParams.MAX_NEW_TOKENS: max_new_tokens,
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.TEMPERATURE: 0.5,
                }
                response = self.watsonx_model.generate_text(prompt=prompt, params=params)
                # a API pode retornar objeto ou string; coerce para string
                return str(response)
            except Exception as e:
                print(f"[ERRO WATSONX] {e}")
                return ""


    def summarize_case(self, save_to_file: bool = True, save_to_firebase: bool = True, page_names: list | None = None, tone: str | None = None, custom_prompt: str | None = None, patient_data: dict | None = None) -> str:
        """Agrega as páginas (ou usa `page_names`) e gera um resumo clínico usando Granite.

        - `page_names`: lista de arquivos em `database/` (ex: ["diario1.txt"]). Se None, usa todas.
        - `patient_data`: dict com dados do formulário — se fornecido, usa ESSAS informações para gerar o resumo (PRIORITÁRIO).
        - Retorna o texto do resumo.
        """

        # Se o médico forneceu dados do formulário, usar isso (prioridade)
        if patient_data:
            # Monta um texto objetivo a partir do formulário para alimentar o modelo
            parts = []
            parts.append("Patient form data (structured):")
            for k, v in patient_data.items():
                parts.append(f"{k}: {v}")
            combined_text = "\n".join(parts)

            # Contextual hint: pedir foco clínico objetivo a partir dos dados fornecidos
            prompt_intro = (
                "You are an experienced clinical assistant. Using ONLY the patient form data below, "
                "generate an objective clinical summary including: brief identification, chief complaint, HPI, "
                "relevant findings, diagnostic impression and brief recommendations. Do not invent additional history."
                "\n\nPatient form data:\n"
            )

            full_prompt = prompt_intro + combined_text

            print("[🔎] Generating clinical summary from patient form data with Granite...")
            summary = self.generate_summary_from_text(full_prompt, max_new_tokens=1024, tone=tone, custom_prompt=custom_prompt)

            # Save to file
            if save_to_file:
                os.makedirs(self.results_path, exist_ok=True)
                out_path = os.path.join(self.results_path, "resumo_clinico_from_form.txt")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                print(f"[💾] Summary (form) saved to: {out_path}")

            # Save to Firebase (optional)
            if save_to_firebase:
                try:
                    save_week_summary({"resumo_clinico_from_form": summary})
                    print("[🔥] Clinical summary (form) sent to Firebase (if configured).")
                except Exception as e:
                    print(f"[ERRO FIREBASE] {e}")

            return summary

        # ----------------------------
        # Fallback: comportamento anterior que usa páginas em database/
        # ----------------------------
        # Carrega páginas
        if page_names is None:
            pages = self.load_pages()
        else:
            pages = {}
            for n in page_names:
                p = os.path.join(self.database_path, n)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        pages[n] = f.read()
                except FileNotFoundError:
                    print(f"Arquivo não encontrado: {p}")

        if not pages:
            print("Nenhuma página para resumir.")
            return ""

        # Monta texto agregando com separadores claros
        combined = []
        for name, text in pages.items():
            combined.append(f"--- INÍCIO: {name} ---\n")
            combined.append(text)
            combined.append(f"\n--- FIM: {name} ---\n\n")

        combined_text = "\n".join(combined)

        # Generate summary
        print("[🔎] Generating clinical summary with Granite...")
        summary = self.generate_summary_from_text(combined_text, max_new_tokens=1024, tone=tone, custom_prompt=custom_prompt)

        # Save to file
        if save_to_file:
            os.makedirs(self.results_path, exist_ok=True)
            out_path = os.path.join(self.results_path, "resumo_clinico.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"[💾] Summary saved to: {out_path}")

        # Save to Firebase (optional)
        if save_to_firebase:
            try:
                save_week_summary({"resumo_clinico": summary})
                print("[🔥] Clinical summary sent to Firebase (if configured).")
            except Exception as e:
                print(f"[ERRO FIREBASE] {e}")

        return summary