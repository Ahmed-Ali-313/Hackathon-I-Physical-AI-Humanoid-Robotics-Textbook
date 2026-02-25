"""
Middleware package for FastAPI application.
"""

from .error_handler import (
    ErrorHandler,
    get_user_friendly_error,
    handle_authentication_error,
    handle_authorization_error,
    handle_not_found_error,
    handle_validation_error,
)

__all__ = [
    "ErrorHandler",
    "get_user_friendly_error",
    "handle_authentication_error",
    "handle_authorization_error",
    "handle_not_found_error",
    "handle_validation_error",
]
