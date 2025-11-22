import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydantic import BaseModel
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
import json
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydantic import BaseModel
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

class GmailSendInput(BaseModel):
    to: str
    subject: str
    body: str
    access_token: str

@tool(permission=ToolPermission.WRITE_ONLY, description="Envia um email usando a API do Gmail")
def send_gmail_email(input: GmailSendInput) -> str:
    # Autenticação com token (mesmo usado para envio)
    creds = Credentials(token=input.access_token)
    service = build('gmail', 'v1', credentials=creds)
    
    # Criar uma mensagem
    message = MIMEText(input.body)
    message['to'] = input.to
    message['subject'] = input.subject
    
    # Codificar a mensagem
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    # Enviar a mensagem
    send_body = {'raw': encoded_message}
    service.users().messages().send(userId='me', body=send_body).execute()
    
    # Armazenar o assunto do email
    subject = input.subject
    
    return subject