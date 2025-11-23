import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydantic import BaseModel
from bs4 import BeautifulSoup
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
import requests
from src.send_email_tool import GmailSendInput, send_gmail_email
from src.read_replies_tool import read_replies
import KeyChain
import streamlit as st


class GmailReadRepliesInput(BaseModel):
    access_token: str
    subject: str


def get_access_token(refresh_token, client_id, client_secret):
    token_uri = "https://oauth2.googleapis.com/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(token_uri, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

def main():
    assunto = "Joao"
    
    kc = KeyChain()
    keys = kc.load_from_env()

    refresh_token = keys["GMAIL_REFRESH_TOKEN"]
    client_id = keys["GMAIL_CLIENT_ID"]
    client_secret = keys["GMAIL_CLIENT_SECRET"]

    access_token = get_access_token(
        refresh_token,
        client_id,
        client_secret
    )
    
    access_token = get_access_token(refresh_token, client_id, client_secret)
    
    if access_token:
        print("Token de acesso obtido com sucesso!")
        print("enviar(1) ou receber(2) email via Gmail API?")
        resp = input()
        if resp == "1":
            input_data = GmailSendInput(
                to='email-teste@gmail.com',
                subject=assunto,
                body='This is a test email.',
                access_token=access_token
            )
            result = send_gmail_email(input_data)
            print(result)
        elif resp == "2":
            input_data = GmailReadRepliesInput(
                access_token=access_token,
                subject=assunto
            )
            result = read_replies(input_data)
            print(result)
        else:
            print("Opção inválida.")
            return
            
    else:
        print("Erro ao obter token de acesso")

if __name__ == '__main__':
    main()