from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository.product_repository import ProductRepository
from app.models import ProductModel, ProductionSubmissionRequest, ProductUpdateRequest

class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def list_products(self, category: Optional[str] = None, status_filter: Optional[str] = None, supplier_id: Optional[str] = None) -> List[ProductModel]:
        return self.repository.get_all(category, status_filter, supplier_id)

    def get_product(self, product_id: str) -> ProductModel:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create_product(self, submission: ProductionSubmissionRequest) -> ProductModel:
        return self.repository.create(submission)

    def update_product(self, product_id: str, product_update: ProductUpdateRequest) -> ProductModel:
        product = self.get_product(product_id)
        update_data = product_update.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"]:
            new_status = str(update_data["status"]).upper()
            if new_status not in ["PENDING", "APPROVED", "REJECTED"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Invalid status. Must be 'PENDING', 'APPROVED', or 'REJECTED'."
                )
            update_data["status"] = new_status
            if new_status == "APPROVED":
                product.rejection_reason = None

        return self.repository.update(product, update_data)

    def delete_product(self, product_id: str) -> dict:
        product = self.get_product(product_id)
        self.repository.delete(product)
        return {"detail": "Product deleted successfully"}