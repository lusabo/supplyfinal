from typing import List, Dict
from sqlalchemy import select, func
from models import Supplier, SupplierMaterial, Category, Material

def buscar_fornecedores(session, material: str, category: str) -> List[Dict]:
    """Retorna fornecedores que atendem simultaneamente à categoria e material."""
    stmt = (
        select(Supplier)
        .join(Supplier.supplier_materials)
        .join(SupplierMaterial.category)
        .join(SupplierMaterial.material)
        .where(func.lower(Category.description).like(func.lower(f"%{category}%")))
        .where(func.lower(Material.description).like(func.lower(f"%{material}%")))
        .distinct()
        .order_by(Supplier.name)
    )
    fornecedores = session.execute(stmt).scalars().all()
    return [
        {"id": f.id, "name": f.name, "email": f.email}
        for f in fornecedores
    ]

def buscar_fornecedores_por_nome(session, name: str) -> List[Dict]:
    """Retorna fornecedor por nome"""
    stmt = (
        select(Supplier)
        .join(Supplier.supplier_materials)
        .where(func.lower(Supplier.name).like(func.lower(f"%{name}%")))
        .distinct()
        .order_by(Supplier.name)
    )
    fornecedores = session.execute(stmt).scalars().all()
    return [
        {"id": f.id, "name": f.name, "email": f.email}
        for f in fornecedores
    ]

def listar_produtos_por_fornecedor(session, supplier_name: str) -> List[Dict]:
    """
    Lista as categorias e materiais fornecidos por um fornecedor específico.
    Retorna uma lista de dicionários: {"categoria": ..., "material": ...}
    """
    stmt = (
        select(Category.description.label("categoria"), Material.description.label("material"))
        .join(SupplierMaterial, SupplierMaterial.category_id == Category.id)
        .join(Material, Material.id == SupplierMaterial.material_id)
        .join(Supplier, Supplier.id == SupplierMaterial.supplier_id)
        .where(func.lower(Supplier.name).like(func.lower(f"%{supplier_name}%")))
        .distinct()
        .order_by(Category.description, Material.description)
    )
    resultados = session.execute(stmt).all()
    return [{"categoria": r.categoria, "material": r.material} for r in resultados]