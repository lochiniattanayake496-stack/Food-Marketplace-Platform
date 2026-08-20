from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    status: str
    

    class Config:
        from_attributes = True

class UserSyncRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    status: str

class UserRoleUpdateRequest(BaseModel):
    role: str