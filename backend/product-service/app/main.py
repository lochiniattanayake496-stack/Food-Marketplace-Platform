import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session  

from app.database import get_db
from app.models import ProductModel
from app.schemas import ProductResponse, ProductionSubmissionRequest, ProoductStatusUpdateRequest, ProductUpdateRequest
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

@app.patch("/api/v1/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str, 
    product_update: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Extract only fields explicitly supplied in the request body
    update_data = product_update.model_dump(exclude_unset=True)

    # Validate status value if status is being updated
    if "status" in update_data:
        new_status = update_data["status"].upper()
        if new_status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid status. Must be 'PENDING', 'APPROVED', or 'REJECTED'."
            )
        update_data["status"] = new_status
        
        # Clear rejection reason if status is changed to APPROVED
        if new_status == "APPROVED":
            product.rejection_reason = None

    # Dynamically apply supplied updates to the database model
    for field, value in update_data.items():
        setattr(product, field, value)

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