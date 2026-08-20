import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session  

from app.database import get_db
from app.models import ProductModel
from app.schemas import ProductResponse, ProductionSubmissionRequest, ProoductStatusUpdateRequest
from app.seed import init_db

app = FastAPI(
    title = "Product Microservice API",
    description = "Handles product catalog management, supplier submissions and Data Steward approvals. ",
    version = "1.0.0",
)

@app.on_event("startup")
def on_startup():
    init_db()

#---GET ALL/FILTERED PRODUCTS ---#

@app.get("/api/v1/products", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Filter products by category"),
    status: Optional[str] = Query(None, description="Filter products by review status (PENDING, APPROVED, REJECTED )"),
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)

    if category:
        query = query.filter(ProductModel.category.ilike(category))
    if status:
        query = query.filter(ProductModel.status == status.upper())

    return query.all()

#--- SUBMIT NEW PRODUCT ---#

@app.post("/api/v1/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def submit_product(submission: ProductionSubmissionRequest, db: Session = Depends(get_db)):
    new_product = ProductModel(
        id=str(uuid.uuid4()),
        name=submission.name,
        description=submission.description,
        price=submission.price,
        category=submission.category,
        status="PENDING",
        supplier_id=submission.supplier_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

#--- GET SINGLE PRODUCT ---#

@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

#--- UPDATE PRODUCT STATUS (DATA STEWARD APPROVAL/REJECTION---#

@app.put("/api/v1/products/{product_id}/status", response_model=ProductResponse)
def update_product_status(
    product_id: str, 
    status_update: ProoductStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_status = status_update.status.upper()
    if new_status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'APPROVED' or 'REJECTED'.")

    product.status = new_status
    if new_status == "REJECTED":
        product.rejection_reason = status_update.rejection_reason
    else:
        product.rejection_reason = None  # Clear rejection reason if approved

    db.commit()
    db.refresh(product)
    return product

#--- DELETE PRODUCT ---#

@app.delete("/api/v1/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}