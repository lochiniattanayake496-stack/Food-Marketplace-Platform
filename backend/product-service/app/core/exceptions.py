"""
Custom application exceptions.

All custom exceptions inherit from AppException, which carries an
explicit HTTP status_code. This lets a single global exception handler
(registered in main.py) convert any of these into a safe, consistent
JSON response — instead of leaking stack traces or internal details
to the client (see "Resilience" requirement in the project guide).

Naming convention: every exception name describes the HTTP-level
outcome (NotFound, Conflict, Forbidden, Validation), not the internal
cause. Keep new exceptions consistent with this pattern.
"""


class AppException(Exception):
    """Base class for all handled application errors.

    Any AppException (or subclass) raised inside a repository/service
    is expected to be caught by the global exception handler in
    main.py and converted into a JSON error response using
    `status_code` and the exception's message.
    """

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    """Raised when an operation conflicts with existing data,
    e.g. a database integrity error (HTTP 409)."""

    def __init__(self, message: str = "Conflict with existing data"):
        super().__init__(message, status_code=409)


class ForbiddenException(AppException):
    """Raised when an authenticated user is not permitted to perform
    the requested action on the target resource (HTTP 403).

    Distinct from an authentication failure (401) — the caller is
    known, but not authorized for this specific action.
    """

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message, status_code=403)


class UnauthorizedException(AppException):
    """Raised when a request has no valid identity/token at all
    (HTTP 401). Reserved for the auth dependency we'll add next —
    not used by the repository/service layer directly."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ValidationException(AppException):
    """Raised for request-level validation failures that Pydantic
    itself can't catch, e.g. an invalid query-parameter value
    (HTTP 400). Replaces the current pattern in ProductRepository.get_all()
    of raising a bare AppException(status_code=400) for an invalid
    status filter — using a named exception here makes intent clearer
    at a glance."""

    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=400)