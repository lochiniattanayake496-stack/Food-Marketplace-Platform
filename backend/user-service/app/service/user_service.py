import logging
from typing import List

from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException
from app.models import UserModel, UserSyncRequest, UserUpdateRequest
from app.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def list_users(self, page: int, limit: int, requester_role: UserRole) -> List[UserModel]:
        # Only a Data Steward has a legitimate reason to browse all
        # user profiles — everyone else only ever fetches their own.
        if requester_role != UserRole.DATA_STEWARD:
            logger.warning("Role %s attempted to list all users", requester_role)
            raise ForbiddenException("Only a Data Steward can list all users")

        offset = (page - 1) * limit
        return self.repository.get_all(offset, limit)

    def get_user(self, user_id: str, requester_id: str, requester_role: UserRole) -> UserModel:
        # A user can view their own profile; a Data Steward can view anyone's.
        if requester_id != user_id and requester_role != UserRole.DATA_STEWARD:
            logger.warning("User %s attempted to view profile %s", requester_id, user_id)
            raise ForbiddenException("You do not have permission to view this profile")

        return self.repository.get_by_id(user_id)

    def sync_user(self, sync_data: UserSyncRequest, current_user_id: str, current_user_role: UserRole) -> UserModel:
        """Called after Cognito login to create/refresh the local
        profile row. id and role come from the authenticated identity,
        never the request body."""
        return self.repository.create_or_sync(
            user_id=current_user_id,
            email=sync_data.email,
            name=sync_data.name,
            role=current_user_role,
        )

    def update_user(self, user_id: str, update: UserUpdateRequest, requester_id: str) -> UserModel:
        # Self-service only — a user may update only their own name.
        # Role/status changes are administrative and not exposed here.
        if requester_id != user_id:
            logger.warning("User %s attempted to update profile %s", requester_id, user_id)
            raise ForbiddenException("You can only update your own profile")

        user = self.repository.get_by_id(user_id)
        update_data = update.model_dump(exclude_unset=True)
        return self.repository.update(user, update_data)

    def deactivate_user(self, user_id: str, requester_id: str, requester_role: UserRole) -> dict:
        # A user can deactivate their own account; a Data Steward can
        # deactivate any account (e.g. for policy violations).
        if requester_id != user_id and requester_role != UserRole.DATA_STEWARD:
            logger.warning("User %s attempted to deactivate profile %s", requester_id, user_id)
            raise ForbiddenException("You do not have permission to deactivate this account")

        user = self.repository.get_by_id(user_id)
        self.repository.deactivate(user)
        return {"detail": "User deactivated successfully"}