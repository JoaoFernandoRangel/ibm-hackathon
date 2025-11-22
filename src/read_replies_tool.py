import json
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydantic import BaseModel
from bs4 import BeautifulSoup
from base64 import urlsafe_b64decode
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
import base64

class GmailReadRepliesInput(BaseModel):
    access_token: str
    subject: str

def get_message_body(msg_data):
    if 'payload' in msg_data:
        payload = msg_data['payload']
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'body' in part and 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if 'body' in payload and 'data' in payload['body']:
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return ''

def extract_user_reply(body):
    soup = BeautifulSoup(body, 'html.parser')
    for element in soup.find_all('div'):
        element.decompose()
    return soup.get_text()

@tool(permission=ToolPermission.READ_ONLY, description="Lê respostas dos emails enviados")
def read_replies(input: GmailReadRepliesInput) -> list:
    # Autenticação com token (mesmo usado para envio)
    creds = Credentials(token=input.access_token)
    service = build('gmail', 'v1', credentials=creds)
    
    # Buscar emails enviados com o assunto especificado
    results = service.users().messages().list(userId='me', q=f"from:me subject:{input.subject}").execute()
    
    messages = results.get('messages', [])
    reply_list = []
    for msg in messages:
        # Buscar conteúdo da mensagem
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()

        
        
        # Buscar respostas para a mensagem
        results_replies = service.users().messages().list(userId='me', q=f"in:inbox subject:re:{input.subject}").execute()
        messages_replies = results_replies.get('messages', [])
        
        for msg_reply in messages_replies:
            # Buscar conteúdo da resposta
            msg_data_reply = service.users().messages().get(userId='me', id=msg_reply['id']).execute()
            
            # Decodificar o corpo da resposta
            body_reply = get_message_body(msg_data_reply)
            
            # Limpar para pegar só a resposta do usuário
            clean = extract_user_reply(body_reply)
            reply_list.append(clean)
    
    return reply_list