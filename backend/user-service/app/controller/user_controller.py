from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, CurrentUser
from app.models import UserResponse, UserSyncRequest, UserUpdateRequest
from app.service.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = UserService(db)
    return service.list_users(page, limit, current_user.role)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def sync_user(
    sync_data: UserSyncRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Creates or refreshes the calling user's own profile — id and
    role always come from the authenticated identity, never the body."""
    service = UserService(db)
    return service.sync_user(sync_data, current_user.id, current_user.role)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = UserService(db)
    return service.get_user(user_id, current_user.id, current_user.role)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = UserService(db)
    return service.update_user(user_id, user_update, current_user.id)


@router.patch("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = UserService(db)
    return service.deactivate_user(user_id, current_user.id, current_user.role)