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
    """Called once after a user's first Cognito login to create their
    local profile row. Deliberately excludes `id` and `role` — id comes
    from the authenticated token (Cognito sub), and role comes from the
    token's Cognito group claim, never from the request body, so a
    caller can't self-assign a privileged role."""
    email: EmailStr
    name: str = Field(..., min_length=1)


class UserUpdateRequest(BaseModel):
    """Self-service profile update. Deliberately excludes `role` and
    `status` — role changes and account activation/deactivation are
    administrative actions, not something a user can do to themselves."""
    name: Optional[str] = Field(None, min_length=1)