from datetime import date
from typing import List
from models import PurchaseRequest, SupplierRequest


def criar_purchase_request(session, category_id: int, material_id: int,
                           specification: str, quantity: int,
                           proposal_deadline: date, delivery_due_date: date) -> PurchaseRequest:
    pr = PurchaseRequest(
        category_id=category_id,
        material_id=material_id,
        specification=specification,
        quantity=quantity,
        proposal_deadline=proposal_deadline,
        delivery_due_date=delivery_due_date,
    )
    session.add(pr)
    session.flush()  # garante pr.id disponível
    return pr

def criar_supplier_requests(session, request_id: int, supplier_ids: List[int]):
    objs = [
        SupplierRequest(supplier_id=sid, request_id=request_id)
        for sid in supplier_ids
    ]
    session.bulk_save_objects(objs, return_defaults=False)