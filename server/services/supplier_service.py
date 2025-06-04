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