from typing import Any, Dict, Optional

class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 404, error_code, details)

class ValidationError(AppError):
    def __init__(
        self,
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 422, error_code, details)

class BadRequestError(AppError):
    def __init__(
        self,
        message: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, error_code, details)

class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 401, error_code, details)

class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Forbidden",
        error_code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 403, error_code, details)

class ConflictError(AppError):
    def __init__(
        self,
        message: str = "Conflict",
        error_code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 409, error_code, details)

class ExternalServiceError(AppError):
    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 502, error_code, details)
