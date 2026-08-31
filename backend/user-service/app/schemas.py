from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    DATA_STEWARD = "DataSteward"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    status: UserStatus = UserStatus.ACTIVE

    class Config:
        from_attributes = True

class UserSyncRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    status: str

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    status: Optional[UserStatus] = None