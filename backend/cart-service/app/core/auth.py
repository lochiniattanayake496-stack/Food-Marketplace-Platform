import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import Header

from app.core.constants import UserRole
from app.core.exceptions import UnauthorizedException, ValidationException

logger = logging.getLogger(__name__)


@dataclass
class CurrentUser:
    id: str
    role: UserRole


def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> CurrentUser:

    if not x_user_id or not x_user_role:
        logger.warning("Request missing required auth headers")
        raise UnauthorizedException("Missing user identity")

    try:
        role = UserRole(x_user_role)
    except ValueError:
        logger.warning("Request sent unrecognized role: %s", x_user_role)
        raise ValidationException(f"Unrecognized role: {x_user_role}")

    return CurrentUser(id=x_user_id, role=role)


def get_current_user_optional(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> Optional[CurrentUser]:
   
    if not x_user_id or not x_user_role:
        return None

    try:
        role = UserRole(x_user_role)
    except ValueError:
        logger.warning("Request sent unrecognized role: %s", x_user_role)
        raise ValidationException(f"Unrecognized role: {x_user_role}")

    return CurrentUser(id=x_user_id, role=role)