import logging
from typing import List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.exceptions import NotFoundException, ConflictException, AppException
from app.models import UserModel, UserStatus

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int, limit: int) -> List[UserModel]:
        try:
            return (
                self.db.query(UserModel)
                .filter(UserModel.status == UserStatus.ACTIVE)
                .offset(offset)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError:
            logger.exception("Database error while listing users")
            raise AppException("Failed to retrieve users", status_code=500)

    def get_by_id(self, user_id: str) -> UserModel:
        try:
            user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        except SQLAlchemyError:
            logger.exception("Database error while fetching user %s", user_id)
            raise AppException("Failed to retrieve user", status_code=500)

        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user

    def get_by_id_or_none(self, user_id: str) -> Optional[UserModel]:
        try:
            return self.db.query(UserModel).filter(UserModel.id == user_id).first()
        except SQLAlchemyError:
            logger.exception("Database error while fetching user %s", user_id)
            raise AppException("Failed to retrieve user", status_code=500)

    def create_or_sync(self, user_id: str, email: str, name: str, role: UserRole) -> UserModel:
        """Idempotent: if the user already exists (e.g. re-sync after
        Cognito attribute change), update instead of erroring."""
        existing = self.get_by_id_or_none(user_id)

        try:
            if existing:
                existing.email = email
                existing.name = name
                user = existing
            else:
                user = UserModel(id=user_id, email=email, name=name, role=role, status=UserStatus.ACTIVE)
                self.db.add(user)

            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error while syncing user %s", user_id)
            raise ConflictException("A user with this email already exists")
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while syncing user %s", user_id)
            raise AppException("Failed to create or sync user", status_code=500)

        logger.info("User synced: %s (%s)", user.id, user.email)
        return user

    def update(self, user: UserModel, update_data: dict) -> UserModel:
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            self.db.commit()
            self.db.refresh(user)
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while updating user %s", user.id)
            raise AppException("Failed to update user", status_code=500)

        logger.info("User updated: %s", user.id)
        return user

    def deactivate(self, user: UserModel) -> None:
        """Soft delete — preserves the row so existing product/cart
        references (supplier_id, customer_id) never dangle."""
        user.status = UserStatus.INACTIVE
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while deactivating user %s", user.id)
            raise AppException("Failed to deactivate user", status_code=500)

        logger.info("User deactivated: %s", user.id)