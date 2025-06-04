from datetime import date
from sqlalchemy import (
    Column, Integer, Text, Date, ForeignKey, UniqueConstraint, Numeric
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False, unique=True)

    supplier_materials = relationship("SupplierMaterial", back_populates="category")
    purchase_requests = relationship("PurchaseRequest", back_populates="category")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False, unique=True)

    supplier_materials = relationship("SupplierMaterial", back_populates="material")
    purchase_requests = relationship("PurchaseRequest", back_populates="material")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)

    supplier_materials = relationship("SupplierMaterial", back_populates="supplier")
    supplier_requests = relationship("SupplierRequest", back_populates="supplier")

class SupplierMaterial(Base):
    __tablename__ = "supplier_materials"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    supplier = relationship("Supplier", back_populates="supplier_materials")
    category = relationship("Category", back_populates="supplier_materials")
    material = relationship("Material", back_populates="supplier_materials")

    __table_args__ = (
        UniqueConstraint("supplier_id", "category_id", "material_id",
                         name="uix_supplier_category_material"),
    )

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    specification = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    proposal_deadline = Column(Date, nullable=False)
    delivery_due_date = Column(Date, nullable=False)

    category = relationship("Category", back_populates="purchase_requests")
    material = relationship("Material", back_populates="purchase_requests")
    supplier_requests = relationship("SupplierRequest", back_populates="purchase_request")

class SupplierRequest(Base):
    __tablename__ = "supplier_requests"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    proposal_value = Column(Numeric(12, 2))

    supplier = relationship("Supplier", back_populates="supplier_requests")
    purchase_request = relationship("PurchaseRequest", back_populates="supplier_requests")

    __table_args__ = (
        UniqueConstraint("supplier_id", "request_id", name="uix_supplier_request"),
    )