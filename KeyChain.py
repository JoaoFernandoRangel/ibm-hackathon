import os
from dotenv import load_dotenv

class KeyChain:
    def __init__(self, env_path: str = None):
        """
        Se env_path for None, o .env padrão será carregado.
        """
        load_dotenv(env_path)

    # -----------------------------------------------------------
    # 1) Buscar tudo do .env
    # -----------------------------------------------------------
    def load_from_streamlit(self):
        keys = {}

        # Gmail OAuth
        keys["GMAIL_CLIENT_ID"] = os.getenv("GMAIL_CLIENT_ID")
        keys["GMAIL_CLIENT_SECRET"] = os.getenv("GMAIL_CLIENT_SECRET")
        keys["GMAIL_REFRESH_TOKEN"] = os.getenv("GMAIL_REFRESH_TOKEN")

        # Gmail API Key simples
        keys["GMAIL_APIKEY"] = os.getenv("GMAIL_APIKEY")

        # Service Account principal
        keys["SERVICE_ACCOUNT_PROJECT_ID"] = os.getenv("SERVICE_ACCOUNT_PROJECT_ID")
        keys["SERVICE_ACCOUNT_PRIVATE_KEY_ID"] = os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID")
        keys["SERVICE_ACCOUNT_PRIVATE_KEY"] = os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY")
        keys["SERVICE_ACCOUNT_EMAIL"] = os.getenv("SERVICE_ACCOUNT_EMAIL")

        # Firebase Admin SDK
        keys["FIREBASE_CLIENT_EMAIL"] = os.getenv("FIREBASE_CLIENT_EMAIL")
        keys["FIREBASE_PRIVATE_KEY"] = os.getenv("FIREBASE_PRIVATE_KEY")
        keys["FIREBASE_PROJECT_ID"] = os.getenv("FIREBASE_PROJECT_ID")

        # Common custom entries (include WATSONX keys)
        keys["WATSONX_APIKEY"] = os.getenv("WATSONX_APIKEY")
        keys["WATSONX_KEY"] = os.getenv("WATSONX_KEY")
        keys["APIKEY"] = os.getenv("APIKEY")

        return keys

    # -----------------------------------------------------------
    # 2) Buscar tudo do st.secrets
    # -----------------------------------------------------------
    def load_from_streamlit(self, st):
        """
        Exemplo de uso:
            import streamlit as st
            kc = KeyChain()
            secrets = kc.load_from_streamlit(st)
        """
        keys = {}

        # Gmail OAuth
        keys["GMAIL_CLIENT_ID"] = st.secrets.get("GMAIL_CLIENT_ID")
        keys["GMAIL_CLIENT_SECRET"] = st.secrets.get("GMAIL_CLIENT_SECRET")
        keys["GMAIL_REFRESH_TOKEN"] = st.secrets.get("GMAIL_REFRESH_TOKEN")

        # Gmail API Key simples
        keys["GMAIL_APIKEY"] = st.secrets.get("GMAIL_APIKEY")

        # Service Account principal
        keys["SERVICE_ACCOUNT_PROJECT_ID"] = st.secrets.get("SERVICE_ACCOUNT_PROJECT_ID")
        keys["SERVICE_ACCOUNT_PRIVATE_KEY_ID"] = st.secrets.get("SERVICE_ACCOUNT_PRIVATE_KEY_ID")
        keys["SERVICE_ACCOUNT_PRIVATE_KEY"] = st.secrets.get("SERVICE_ACCOUNT_PRIVATE_KEY")
        keys["SERVICE_ACCOUNT_EMAIL"] = st.secrets.get("SERVICE_ACCOUNT_EMAIL")

        # Firebase Admin SDK
        keys["FIREBASE_CLIENT_EMAIL"] = st.secrets.get("FIREBASE_CLIENT_EMAIL")
        keys["FIREBASE_PRIVATE_KEY"] = st.secrets.get("FIREBASE_PRIVATE_KEY")
        keys["FIREBASE_PROJECT_ID"] = st.secrets.get("FIREBASE_PROJECT_ID")

        # Common custom entries (include WATSONX keys)
        keys["WATSONX_APIKEY"] = st.secrets.get("WATSONX_APIKEY")
        keys["WATSONX_KEY"] = st.secrets.get("WATSONX_KEY")
        keys["APIKEY"] = st.secrets.get("APIKEY")

        return keys

'''
Exemplo de uso:
kc = KeyChain(".env")
keys = kc.load_from_streamlit()
print(keys["GMAIL_CLIENT_ID"])

#Ou, para Streamlit:
import streamlit as st
kc = KeyChain()
keys = kc.load_from_streamlit(st)
'''