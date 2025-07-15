# Standard library imports
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

# Third-party imports
from dotenv import load_dotenv
from fastmcp import FastMCP

# Local imports
from db import session_scope
from models import Category, Material, Supplier
from services import supplier_service

# Load environment variables
load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
TEMPLATE_PATH =  "../templates/email_proposta.html"

# Initialize the FastMCP server
mcp = FastMCP("Supply Chain Assistant")

@mcp.tool()
def list_categories() -> List[str]:
    """List all available categories in the system."""
    with session_scope() as session:
        categories = session.query(Category).all()
        return [category.description for category in categories]

@mcp.tool()
def list_materials() -> List[str]:
    """List all available materials in the system."""
    with session_scope() as session:
        materials = session.query(Material).all()
        return [material.description for material in materials]

@mcp.tool()
def list_suppliers() -> List[str]:
    """List all registered suppliers in the system."""
    with session_scope() as session:
        suppliers = session.query(Supplier).all()
        return [supplier.name for supplier in suppliers]

@mcp.tool()
def find_supplier_by_name(name: str) -> Optional[dict]:
    """Find a supplier by their name."""
    with session_scope() as session:
        suppliers = supplier_service.buscar_fornecedores_por_nome(session, name)
        if suppliers:
            return suppliers[0]
        return None

@mcp.tool()
def find_suppliers_by_category_and_material(category: str, material: str) -> List[dict]:
    """Find suppliers that provide specific category and material (case insensitive)."""
    with session_scope() as session:
        return supplier_service.buscar_fornecedores(session, material, category)

@mcp.tool()
def send_rfq_email(
    recipient: str,
    fornecedor: str,
    categoria: str,
    material: str,
    quantidade: str,
    especificacao: str,
    prazo: str
) -> str:
    """
    Send RFQ (Request for Quotation) email.
    
    Args:
        recipient: supplier email
        fornecedor: supplier name
        categoria: item category
        material: material description
        quantidade: requested quantity
        especificacao: technical specification
        prazo: proposal deadline
    Returns:
        string confirming success or error
    """
    try:
        print(f"Sending RFQ email to {recipient} for {fornecedor} - {categoria} - {material}")
        html_body = render_email_html(
            fornecedor=fornecedor,
            categoria=categoria,
            material=material,
            quantidade=quantidade,
            especificacao=especificacao,
            prazo=prazo,
            remetente_email=GMAIL_ADDRESS
        )
        
        msg = EmailMessage()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = f"RFQ: {categoria} - {material}"
        msg.set_content(html_body, subtype="html")
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"RFQ email sent successfully to {recipient}")
            
        return f"RFQ email sent successfully to {recipient}"
        
    except Exception as e:
        print(f"Error sending RFQ email: {str(e)}")
        return f"Error sending email: {str(e)}"

def render_email_html(**kwargs) -> str:
    print(f"Rendering email HTML with placeholders: {kwargs}")
    """
    Read email template and replace placeholders with provided values.
    
    Args:
        **kwargs: Dictionary of placeholder names and their values to replace in template
        
    Returns:
        str: Rendered HTML content
        
    Raises:
        ValueError: If template file not found or missing required placeholder
    """
    try:
        # Read template file
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
            html = file.read()
        
        # Replace placeholders with values
        return html.format(**kwargs)
        
    except FileNotFoundError:
        print(f"Template file not found at: {TEMPLATE_PATH}")
        raise ValueError(f"Email template not found at: {TEMPLATE_PATH}")
    except KeyError as e:
        print(f"Missing required placeholder in template: {e}")
        raise ValueError(f"Missing required placeholder in template: {e}")

@mcp.tool()
def list_products_by_supplier(supplier_name: str) -> List[str]:
    """
    Lista os produtos/materiais fornecidos por um fornecedor específico.
    """
    with session_scope() as session:
        return supplier_service.listar_produtos_por_fornecedor(session, supplier_name)

# Start the server
if __name__ == "__main__":
    mcp.run(host="localhost", port=8000)