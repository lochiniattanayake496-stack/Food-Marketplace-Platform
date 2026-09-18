import logging
import uuid
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException, AppException, ValidationException
from app.models import ProductModel, ProductSubmissionRequest, ProductStatus

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        supplier_id: Optional[str] = None,
        show_all_statuses: bool = False,
    ) -> List[ProductModel]:
        query = self.db.query(ProductModel)

        if category:
            query = query.filter(ProductModel.category.ilike(category))

        if status:
            try:
                status_enum = ProductStatus(status.upper())
            except ValueError:
                logger.warning("Invalid status filter received: %s", status)
                raise ValidationException(f"Invalid status filter: {status}")
            query = query.filter(ProductModel.status == status_enum)
        elif not show_all_statuses:
            # No status filter given, and caller isn't viewing their own
            # full history: default to APPROVED only, so "no filter"
            # never accidentally means "show everything" — required by
            # the guide's Product visibility rule.
            query = query.filter(ProductModel.status == ProductStatus.APPROVED)
        # else: show_all_statuses=True and no explicit status — a
        # supplier viewing their own products' approval history, don't
        # filter by status at all.

        if supplier_id:
            query = query.filter(ProductModel.supplier_id == supplier_id)

        query = query.filter(ProductModel.is_active.is_(True))

        try:
            return query.all()
        except SQLAlchemyError:
            logger.exception("Database error while listing products")
            raise AppException("Failed to retrieve products", status_code=500)

    def get_by_id(self, product_id: str) -> ProductModel:
        try:
            product = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product_id)
                .first()
            )
        except SQLAlchemyError:
            logger.exception("Database error while fetching product %s", product_id)
            raise AppException("Failed to retrieve product", status_code=500)

        if not product:
            logger.info("Product not found: %s", product_id)
            raise NotFoundException(f"Product {product_id} not found")

        return product

    def create(self, submission: ProductSubmissionRequest, supplier_id: str) -> ProductModel:
        new_product = ProductModel(
            id=str(uuid.uuid4()),
            name=submission.name,
            description=submission.description,
            price=submission.price,
            category=submission.category,
            stock=submission.stock,
            status=ProductStatus.PENDING,
            is_active=True,
            supplier_id=supplier_id,
        )
        try:
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error while creating product")
            raise ConflictException("Product could not be created due to a data conflict")
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while creating product")
            raise AppException("Failed to create product", status_code=500)

        logger.info("Product created: %s by supplier %s", new_product.id, supplier_id)
        return new_product

    def update(self, product: ProductModel, update_data: dict) -> ProductModel:
        for field, value in update_data.items():
            setattr(product, field, value)

        try:
            self.db.commit()
            self.db.refresh(product)
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error while updating product %s", product.id)
            raise ConflictException("Product could not be updated due to a data conflict")
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while updating product %s", product.id)
            raise AppException("Failed to update product", status_code=500)

        logger.info("Product updated: %s", product.id)
        return product

    def deactivate(self, product: ProductModel) -> None:
        """Soft delete — flips is_active rather than removing the row,
        preserving audit history per the guide's requirements."""
        product.is_active = False
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while deactivating product %s", product.id)
            raise AppException("Failed to deactivate product", status_code=500)

        logger.info("Product deactivated: %s", product.id)