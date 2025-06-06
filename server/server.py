from db import session_scope
from fastmcp import FastMCP
from models import Category, Material
from services import supplier_service

mcp = FastMCP("MCP Server")

@mcp.tool()
def list_suppliers(category: str, material: str):
    """List suppliers based on the provided category and material."""
    with session_scope() as session:
        return supplier_service.buscar_fornecedores(session, material, category)


@mcp.tool()
def list_categories():
    """List all available categories."""
    with session_scope() as session:
        return [category.description for category in session.query(Category).all()]


@mcp.tool()
def list_materials():
    """List all available materials."""
    with session_scope() as session:
        return [material.description for material in session.query(Material).all()]
