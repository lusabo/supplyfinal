from fastmcp import FastMCP
from db import session_scope
from services import request_service, supplier_service, email_service
from models import Category, Material
import os
from pathlib import Path

mcp = FastMCP("MCP Server")

@mcp.resource("fornecedores://{category}/{material}")
def listar_fornecedores(category: str, material: str):
    with session_scope() as session:
        return supplier_service.buscar_fornecedores(session, material, category)
    
# -------------------------------------------------------------------------
# Tool: criar nova solicitação, vincular fornecedores e enviar e‑mails
# -------------------------------------------------------------------------
TEMPLATE_PATH = Path("templates/email_proposta.html")
TEMPLATE = TEMPLATE_PATH.read_text() if TEMPLATE_PATH.exists() else "<p>Template não encontrado</p>"

@mcp.tool()
def nova_solicitacao(category_id: int, material_id: int, specification: str,
                     quantity: int, proposal_deadline: str, delivery_due_date: str) -> str:
    with session_scope() as session:
        pr = request_service.criar_purchase_request(
            session,
            category_id, material_id,
            specification, quantity,
            proposal_deadline, delivery_due_date,
        )

        # Busca descrições para exibir e filtrar
        cat_desc = session.get(Category, category_id).description
        mat_desc = session.get(Material, material_id).description

        fornecedores = supplier_service.buscar_fornecedores(session, mat_desc, cat_desc)
        supplier_ids = [f["id"] for f in fornecedores]
        request_service.criar_supplier_requests(session, pr.id, supplier_ids)

        # Envia e‑mails (mantém lógica pré‑existente)
        for forn in fornecedores:
            ctx = {
                "remetente_email": os.getenv("EMAIL_REMETENTE", "compras@empresa.com"),
                "assunto": f"Solicitação {pr.id} - {mat_desc}",
                "fornecedor": forn["name"],
                "categoria": cat_desc,
                "material": mat_desc,
                "quantidade": quantity,
                "especificacao": specification,
                "prazo": proposal_deadline,
            }
            email_service.enviar_email_solicitacao(forn["email"], TEMPLATE, ctx)

    return f"Solicitação {pr.id} criada e {len(fornecedores)} e‑mails enviados."