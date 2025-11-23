import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
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


class GmailSendWithAttachmentInput(BaseModel):
    to: str
    subject: str
    body: str
    access_token: str
    attachment_bytes_base64: str  # base64 encoded
    attachment_filename: str


@tool(permission=ToolPermission.WRITE_ONLY, description="Send an email with an attachment (Gmail API)")
def send_gmail_email_with_ics(input: GmailSendWithAttachmentInput) -> str:
    """Send an email with a binary attachment (e.g., .ics calendar invite) using Gmail API.

    - `attachment_bytes_base64` should be a base64-encoded bytes string of the attachment.
    - Returns the subject on success.
    """
    creds = Credentials(token=input.access_token)
    service = build('gmail', 'v1', credentials=creds)

    # Build multipart message with attachment
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders

    msg = MIMEMultipart()
    msg['to'] = input.to
    msg['subject'] = input.subject

    # body part
    body_part = MIMEText(input.body, 'plain')
    msg.attach(body_part)

    # attachment part
    attachment_data = base64.b64decode(input.attachment_bytes_base64)
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{input.attachment_filename}"')
    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

    return input.subject

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

    # Prefer requests if available, else fallback to urllib
    try:
        import requests  # local import to avoid NameError if missing earlier
    except Exception:
        requests = None

    if requests:
        try:
            response = requests.post(token_uri, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            # include response text when available for debugging
            msg = getattr(e, "response", None)
            raise RuntimeError(f"Failed to obtain access token via requests: {e} {getattr(msg,'text', '')}")
    else:
        # Fallback using urllib
        try:
            import urllib.request
            import urllib.parse
            import json as _json

            encoded = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(token_uri, data=encoded, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                parsed = _json.loads(body)
                return parsed.get("access_token")
        except Exception as e:
            raise RuntimeError(f"Failed to obtain access token via urllib fallback: {e}")