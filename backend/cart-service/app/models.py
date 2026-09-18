from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


# ==========================================
# 1. SQLAlchemy Database Models
# ==========================================

class CartModel(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, index=True)
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False)  # was Integer — mismatched CartModel.id (String)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # snapshot of product price at time of add — never client-supplied

    cart = relationship("CartModel", back_populates="items")


# ==========================================
# 2. Pydantic Schemas (DTOs)
# ==========================================

class CartItemResponse(BaseModel):
    product_id: str = Field(..., alias="productId")
    product_name: str = Field(..., alias="productName")
    quantity: int
    unit_price: float = Field(..., alias="unitPrice")

    class Config:
        from_attributes = True
        populate_by_name = True


class CartResponse(BaseModel):
    id: str
    customer_id: str = Field(..., alias="customerId")
    items: List[CartItemResponse] = []
    total_price: float = Field(0.0, alias="totalPrice")

    class Config:
        from_attributes = True
        populate_by_name = True


class AddCartItemRequest(BaseModel):
    product_id: str = Field(..., alias="productId")
    quantity: int = Field(..., ge=1)

    class Config:
        populate_by_name = True


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1)

    class Config:
        populate_by_name = True