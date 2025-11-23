"""Obter token de acesso OAuth do Gmail (modo de desenvolvimento).

Exigências:
- Crie credenciais OAuth do tipo "Desktop app" no Google Cloud Console.
- Baixe o arquivo `client_secret.json` e coloque em `segredos/client_secret.json`.

Uso:
1) Ative o venv: `.\.venv\Scripts\Activate.ps1`
2) Execute: `python .\scripts\get_gmail_token.py`
3) O script abrirá o navegador para autorizar e gravará `segredos/gmail_credentials.json` com tokens.

Observação: este token expira; para produção use refresh tokens armazenados com segurança.
"""
import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'openid',
    'email',
    'profile'
]

CLIENT_SECRET_PATH = os.path.join('segredos', 'client_secret.json')
OUTPUT_PATH = os.path.join('segredos', 'gmail_credentials.json')


def main():
    if not os.path.exists(CLIENT_SECRET_PATH):
        print(f"Arquivo de credenciais não encontrado: {CLIENT_SECRET_PATH}")
        print("Crie credenciais OAuth no Google Cloud Console e salve como segredos/client_secret.json")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0)

    data = {
        'token': creds.token,
        'refresh_token': getattr(creds, 'refresh_token', None),
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
    }

    os.makedirs('segredos', exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Credenciais salvas em: {OUTPUT_PATH}")
    print("Use o campo 'Gmail OAuth access token' na UI ou copie o campo 'token' do arquivo gerado.")


if __name__ == '__main__':
    main()
