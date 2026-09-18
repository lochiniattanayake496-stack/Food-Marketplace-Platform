import enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Enum as SqlEnum

from app.core.constants import UserRole
from app.database import Base


# ==========================================
# 1. Enums
# ==========================================

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ==========================================
# 2. SQLAlchemy Database Model
# ==========================================

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Cognito 'sub' — never client-generated
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False)
    status = Column(SqlEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)


# ==========================================
# 3. Pydantic Schemas (DTOs)
# ==========================================

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    status: UserStatus

    class Config:
        from_attributes = True


class UserSyncRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1)


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1)