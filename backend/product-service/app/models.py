from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Float
from app.database import Base

# ==========================================
# 1. SQLAlchemy Database Models
# ==========================================

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    supplier_id = Column(String, nullable=False, index=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(
        String,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )


# ==========================================
# 2. Pydantic Schemas (DTOs)
# ==========================================

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    status: str
    supplier_id: str = Field(..., alias="supplierId")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        from_attributes = True
        populate_by_name = True


class ProductionSubmissionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    supplier_id: str = Field(..., alias="supplierId")

    class Config:
        populate_by_name = True


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    status: Optional[str] = None
    supplier_id: Optional[str] = Field(None, alias="supplierId")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        populate_by_name = True


class ProductStatusUpdateRequest(BaseModel):
    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        populate_by_name = True