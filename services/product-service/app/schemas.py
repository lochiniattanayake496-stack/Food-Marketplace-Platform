from pydantic import BaseModel, Field
from typing import Optional

class ProductResponse(BaseModel):
    id:str
    name: str
    description: Optional[str] = None
    price: float
    category:str
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
    category:str
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

class ProoductStatusUpdateRequest(BaseModel):
    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")

    class Config:
        populate_by_name = True


  
    