import os
import json
import torch

# Watsonx
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Local Granite
from transformers import AutoTokenizer, AutoModelForCausalLM
# Adicione essencialmente APÓS seus imports:
from src.firebase_db import save_page_result, save_week_summary



class DiaryAnalyzer:

    def __init__(
        self,
        backend="local",
        database_path="database",
        results_path="results",

        # Local Granite
        local_model_name="ibm-granite/granite-3.0-2b-instruct",

        # Watsonx Granite
        watsonx_model="ibm/granite-13b-chat-v2",
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
            }

            self.watsonx_model = Model(
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