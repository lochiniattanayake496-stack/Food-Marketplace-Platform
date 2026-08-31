from pydantic import BaseModel, Field
from typing import List, Optional

class CartItemResponse(BaseModel):
    productId: str = Field(..., alias="product_id")
    productName: str = Field(..., alias="product_name")
    quantity: int
    unitPrice: float = Field(..., alias="unit_price")

    class Config:
        from_attributes = True
        populate_by_name = True

class CartResponse(BaseModel):
    id: str
    cartId: Optional[str] = Field(None, alias="id")
    customerId: str = Field(..., alias="customer_id")
    items: List[CartItemResponse] = []
    totalPrice: float = 0.0

    class Config:
        from_attributes = True
        populate_by_name = True

class AddCartItemRequest(BaseModel):
    productId: str = Field(..., alias="product_id")
    productName: Optional[str] = Field("Item", alias="product_name")
    unitPrice: Optional[float] = Field(1.0, alias="unit_price")
    quantity: int = Field(..., ge=1)

    class Config:
        populate_by_name = True

class UpdateCartItemRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)
    unitPrice: Optional[float] = Field(None, gt=0, alias="unit_price")
    productName: Optional[str] = Field(None, alias="product_name")

    class Config:
        populate_by_name = True