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
    """FastAPI dependency — inject with `Depends(get_current_user)`.

    Headers are declared Optional here so FastAPI lets the request
    through even when they're missing, and we raise our own
    UnauthorizedException (401) instead — otherwise FastAPI's own
    built-in validation would reject a missing required header with
    a generic 422 before this function body ever runs.

    Use this for routes where identity is always required.
    """
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
    """FastAPI dependency — inject with `Depends(get_current_user_optional)`.

    Like get_current_user, but returns None instead of raising when
    headers are absent entirely, rather than treating that as an
    error. Use this for routes that work anonymously by default (e.g.
    public product browsing) but need to know the caller's identity
    IF they're present — for example, to gate an optional
    privileged query parameter behind a role check.

    A malformed/unrecognized role is still treated as an error even
    here, since that's not "no identity" — it's "identity was sent,
    but it's invalid."
    """
    if not x_user_id or not x_user_role:
        return None

    try:
        role = UserRole(x_user_role)
    except ValueError:
        logger.warning("Request sent unrecognized role: %s", x_user_role)
        raise ValidationException(f"Unrecognized role: {x_user_role}")

    return CurrentUser(id=x_user_id, role=role)