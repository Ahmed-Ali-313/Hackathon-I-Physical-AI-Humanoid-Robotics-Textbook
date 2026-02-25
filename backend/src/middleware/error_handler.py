"""
Error handling middleware for FastAPI.

Provides user-friendly error messages for common failure scenarios.
"""

from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from qdrant_client.http.exceptions import UnexpectedResponse
import logging

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Middleware for handling errors and returning user-friendly messages.
    """

    @staticmethod
    async def handle_error(request: Request, call_next: Callable) -> Response:
        """
        Handle errors and return user-friendly messages.

        Args:
            request: FastAPI request
            call_next: Next middleware in chain

        Returns:
            Response with error message if error occurred
        """
        try:
            response = await call_next(request)
            return response

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "The database is temporarily unavailable. Please try again in a few moments.",
                    "error_type": "database_error",
                },
            )

        except UnexpectedResponse as e:
            logger.error(f"Qdrant error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "The search service is temporarily unavailable. Please try again in a few moments.",
                    "error_type": "search_service_error",
                },
            )

        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "Unable to connect to external services. Please check your connection and try again.",
                    "error_type": "connection_error",
                },
            )

        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "detail": "The request took too long to complete. Please try again.",
                    "error_type": "timeout_error",
                },
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An unexpected error occurred. Please try again later.",
                    "error_type": "internal_error",
                },
            )


def get_user_friendly_error(error: Exception) -> dict:
    """
    Convert exception to user-friendly error message.

    Args:
        error: Exception that occurred

    Returns:
        Dictionary with error details
    """
    error_messages = {
        "SQLAlchemyError": "The database is temporarily unavailable. Please try again in a few moments.",
        "UnexpectedResponse": "The search service is temporarily unavailable. Please try again in a few moments.",
        "ConnectionError": "Unable to connect to external services. Please check your connection and try again.",
        "TimeoutError": "The request took too long to complete. Please try again.",
        "ValueError": "Invalid input provided. Please check your data and try again.",
        "KeyError": "Required information is missing. Please try again.",
    }

    error_type = type(error).__name__
    message = error_messages.get(error_type, "An unexpected error occurred. Please try again later.")

    return {
        "detail": message,
        "error_type": error_type.lower(),
    }


def handle_authentication_error() -> JSONResponse:
    """
    Return authentication error response.

    Returns:
        JSON response with authentication error
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Your session has expired. Please log in again.",
            "error_type": "authentication_expired",
            "action": "redirect_to_login",
        },
    )


def handle_authorization_error() -> JSONResponse:
    """
    Return authorization error response.

    Returns:
        JSON response with authorization error
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": "You don't have permission to access this resource.",
            "error_type": "authorization_error",
        },
    )


def handle_not_found_error(resource: str = "Resource") -> JSONResponse:
    """
    Return not found error response.

    Args:
        resource: Name of resource that wasn't found

    Returns:
        JSON response with not found error
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": f"{resource} not found.",
            "error_type": "not_found",
        },
    )


def handle_validation_error(message: str) -> JSONResponse:
    """
    Return validation error response.

    Args:
        message: Validation error message

    Returns:
        JSON response with validation error
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": message,
            "error_type": "validation_error",
        },
    )
