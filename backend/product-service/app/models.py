import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Enum as SqlEnum
from app.database import Base


# ==========================================
# 1. Enums
# ==========================================

class ProductStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ==========================================
# 2. SQLAlchemy Database Models
# ==========================================

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    status = Column(SqlEnum(ProductStatus), nullable=False, default=ProductStatus.PENDING, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    supplier_id = Column(String, nullable=False, index=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==========================================
# 3. Pydantic Schemas (DTOs)
# ==========================================

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    category: str
    stock: int
    status: ProductStatus
    is_active: bool = Field(..., alias="isActive")
    supplier_id: str = Field(..., alias="supplierId")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        from_attributes = True
        populate_by_name = True


class ProductSubmissionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str
    stock: int = Field(0, ge=0)

    class Config:
        populate_by_name = True


class ProductUpdateRequest(BaseModel):
    """Supplier-facing update. Deliberately excludes `status` and `supplier_id` —
    status changes go through ProductStatusUpdateRequest (Data Steward only),
    and ownership is never client-editable."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)

    class Config:
        populate_by_name = True


class ProductStatusUpdateRequest(BaseModel):
    """Data Steward-only: approve/reject a submission."""
    status: ProductStatus
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        populate_by_name = True