from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ProductResponse, ProductionSubmissionRequest, ProductUpdateRequest
from app.service.product_service import ProductService

# Base path is defined here:
router = APIRouter(prefix="/api/v1/products", tags=["Products"])

# GET /api/v1/products (Base path)
@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Filter products by category"),
    status: Optional[str] = Query(None, description="Filter products by review status (PENDING, APPROVED, REJECTED)"),
    supplier_id: Optional[str] = Query(None, description="Filter products by supplier ID"),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    return service.list_products(category, status, supplier_id)

# POST /api/v1/products (Base path)
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def submit_product(submission: ProductionSubmissionRequest, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create_product(submission)

# GET /api/v1/products/{product_id}
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product(product_id)

# PATCH /api/v1/products/{product_id}
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, product_update: ProductUpdateRequest, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update_product(product_id, product_update)

# DELETE /api/v1/products/{product_id}
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.delete_product(product_id)