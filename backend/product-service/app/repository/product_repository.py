import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import ProductModel, ProductionSubmissionRequest, ProductUpdateRequest

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, category: Optional[str] = None, status: Optional[str] = None, supplier_id: Optional[str] = None) -> List[ProductModel]:
        query = self.db.query(ProductModel)
        if category:
            query = query.filter(ProductModel.category.ilike(category))
        if status:
            query = query.filter(ProductModel.status.ilike(status))
        if supplier_id:
            query = query.filter(ProductModel.supplier_id == supplier_id)
        return query.all()

    def get_by_id(self, product_id: str) -> Optional[ProductModel]:
        return self.db.query(ProductModel).filter(ProductModel.id == product_id).first()

    def create(self, submission: ProductionSubmissionRequest) -> ProductModel:
        new_product = ProductModel(
            id=str(uuid.uuid4()),
            name=submission.name,
            description=submission.description,
            price=submission.price,
            category=submission.category,
            status="PENDING",
            supplier_id=submission.supplier_id
        )
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product

    def update(self, product: ProductModel, update_data: dict) -> ProductModel:
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: ProductModel) -> None:
        self.db.delete(product)
        self.db.commit()