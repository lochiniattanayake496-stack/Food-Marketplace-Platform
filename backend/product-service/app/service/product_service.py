import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.constants import UserRole
from app.core.auth import CurrentUser
from app.models import (
    ProductModel,
    ProductSubmissionRequest,
    ProductUpdateRequest,
    ProductStatusUpdateRequest,
    ProductStatus,
)
from app.repository.product_repository import ProductRepository

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def list_products(
        self,
        category: Optional[str] = None,
        status_filter: Optional[str] = None,
        supplier_id: Optional[str] = None,
    ) -> List[ProductModel]:
        return self.repository.get_all(category, status_filter, supplier_id)

    def get_product(self, product_id: str) -> ProductModel:
        """Raw internal fetch — no visibility restriction. Used by
        update/review/deactivate, which already enforce their own
        ownership/role checks and legitimately need to load a product
        regardless of its current status (e.g. a supplier must be able
        to fetch their own PENDING product to edit it)."""
        return self.repository.get_by_id(product_id)

    def get_visible_product(self, product_id: str, current_user: Optional[CurrentUser]) -> ProductModel:
        """Public-facing fetch for GET /{product_id}. Enforces the
        guide's visibility rule: an APPROVED + active product is visible
        to anyone, but a PENDING/REJECTED/deactivated product is only
        visible to its owning supplier or a Data Steward. Returns
        NotFoundException (not Forbidden) for anyone else, so the
        response doesn't confirm a restricted product's existence to
        an unauthorized caller."""
        product = self.repository.get_by_id(product_id)

        is_publicly_visible = product.status == ProductStatus.APPROVED and product.is_active
        if is_publicly_visible:
            return product

        if current_user is None:
            raise NotFoundException(f"Product {product_id} not found")

        is_owner = current_user.role == UserRole.SUPPLIER and current_user.id == product.supplier_id
        is_steward = current_user.role == UserRole.DATA_STEWARD
        if is_owner or is_steward:
            return product

        raise NotFoundException(f"Product {product_id} not found")

    def create_product(self, submission: ProductSubmissionRequest, supplier_id: str) -> ProductModel:
        product = self.repository.create(submission, supplier_id)
        logger.info("Supplier %s created product %s", supplier_id, product.id)
        return product

    def update_product(
        self,
        product_id: str,
        product_update: ProductUpdateRequest,
        current_supplier_id: str,
    ) -> ProductModel:
        product = self.get_product(product_id)

        if product.supplier_id != current_supplier_id:
            logger.warning(
                "Supplier %s attempted to update product %s owned by %s",
                current_supplier_id, product_id, product.supplier_id,
            )
            raise ForbiddenException("You do not have permission to modify this product")

        update_data = product_update.model_dump(exclude_unset=True)
        updated = self.repository.update(product, update_data)
        logger.info("Supplier %s updated product %s", current_supplier_id, product_id)
        return updated

    def review_product(
        self,
        product_id: str,
        status_update: ProductStatusUpdateRequest,
        reviewer_role: str,
    ) -> ProductModel:
        """Data Steward-only: approve or reject a submission."""
        if reviewer_role != UserRole.DATA_STEWARD:
            logger.warning("Role %s attempted to review product %s", reviewer_role, product_id)
            raise ForbiddenException("Only a Data Steward can review submissions")

        product = self.get_product(product_id)

        update_data = {"status": status_update.status}
        if status_update.status == ProductStatus.REJECTED:
            update_data["rejection_reason"] = status_update.rejection_reason
        else:
            update_data["rejection_reason"] = None

        updated = self.repository.update(product, update_data)
        logger.info("Product %s reviewed -> %s", product_id, status_update.status)
        return updated

    def deactivate_product(self, product_id: str, current_supplier_id: str) -> dict:
        product = self.get_product(product_id)

        if product.supplier_id != current_supplier_id:
            logger.warning(
                "Supplier %s attempted to deactivate product %s owned by %s",
                current_supplier_id, product_id, product.supplier_id,
            )
            raise ForbiddenException("You do not have permission to remove this product")

        self.repository.deactivate(product)
        logger.info("Supplier %s deactivated product %s", current_supplier_id, product_id)
        return {"detail": "Product deactivated successfully"}