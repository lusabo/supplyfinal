# services/email_service.py
import base64
from email.mime.text import MIMEText

def enviar_email_solicitacao(gmail_service, fornecedor_email: str, dados_solicitacao: dict):
    """Envia um e-mail de solicitação de proposta para o fornecedor especificado."""
    # Carrega template de email (HTML) e preenche campos dinamicamente
    with open("templates/email_proposta.html") as f:
        template = f.read()
    conteudo = template.format(**dados_solicitacao)
    
    # Monta a mensagem MIME
    msg = MIMEText(conteudo, "html", "utf-8")
    msg["to"] = fornecedor_email
    msg["from"] = dados_solicitacao.get("remetente_email")  # email do solicitante
    msg["subject"] = f"Solicitação de Proposta - {dados_solicitacao.get('titulo')}"
    
    # Codifica em base64 conforme exigido pela Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    body = {"raw": raw}
    # Envia o e-mail usando a API do Gmail
    gmail_service.users().messages().send(userId="me", body=body).execute()
