from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, get_current_user_optional, CurrentUser
from app.core.constants import UserRole
from app.models import (
    ProductResponse,
    ProductSubmissionRequest,
    ProductUpdateRequest,
    ProductStatusUpdateRequest,
)
from app.service.product_service import ProductService
from app.core.exceptions import ForbiddenException

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter products by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by review status (PENDING, APPROVED, REJECTED) — restricted, see below"),
    supplier_id: Optional[str] = Query(None, description="Filter products by supplier ID"),
    db: Session = Depends(get_db),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    if status_filter:
        is_steward = current_user is not None and current_user.role == UserRole.DATA_STEWARD
        # A supplier may use the status filter only when also scoping to
        # their own supplier_id — i.e. checking their own submissions'
        # approval status, not browsing everyone else's.
        is_supplier_viewing_own = (
            current_user is not None
            and current_user.role == UserRole.SUPPLIER
            and supplier_id == current_user.id
        )
        if not (is_steward or is_supplier_viewing_own):
            raise ForbiddenException(
                "Only a Data Steward can filter by review status, "
                "or a Supplier filtering their own products"
            )

    service = ProductService(db)
    return service.list_products(category, status_filter, supplier_id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
):
    service = ProductService(db)
    return service.get_visible_product(product_id, current_user)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def submit_product(
    submission: ProductSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db)
    return service.create_product(submission, current_user.id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_update: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db)
    return service.update_product(product_id, product_update, current_user.id)


@router.patch("/{product_id}/review", response_model=ProductResponse)
def review_product_submission(
    product_id: str,
    status_update: ProductStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db)
    return service.review_product(product_id, status_update, current_user.role)


@router.patch("/{product_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db)
    return service.deactivate_product(product_id, current_user.id)