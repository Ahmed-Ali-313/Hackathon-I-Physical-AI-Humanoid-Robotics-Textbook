"""
Tests for error handling middleware.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from qdrant_client.http.exceptions import UnexpectedResponse
from src.middleware.error_handler import (
    ErrorHandler,
    get_user_friendly_error,
    handle_authentication_error,
    handle_authorization_error,
    handle_not_found_error,
    handle_validation_error,
)


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()

    @app.get("/test-database-error")
    async def test_database_error():
        raise SQLAlchemyError("Database connection failed")

    @app.get("/test-qdrant-error")
    async def test_qdrant_error():
        raise UnexpectedResponse(status_code=500, reason_phrase="Internal Server Error")

    @app.get("/test-connection-error")
    async def test_connection_error():
        raise ConnectionError("Connection refused")

    @app.get("/test-timeout-error")
    async def test_timeout_error():
        raise TimeoutError("Request timeout")

    @app.get("/test-unexpected-error")
    async def test_unexpected_error():
        raise RuntimeError("Unexpected error")

    @app.get("/test-success")
    async def test_success():
        return {"message": "success"}

    # Add error handling middleware
    app.middleware("http")(ErrorHandler.handle_error)

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_database_error_returns_503(client):
    """Test database error returns 503 with user-friendly message."""
    response = client.get("/test-database-error")

    assert response.status_code == 503
    assert "database is temporarily unavailable" in response.json()["detail"].lower()
    assert response.json()["error_type"] == "database_error"


def test_qdrant_error_returns_503(client):
    """Test Qdrant error returns 503 with user-friendly message."""
    response = client.get("/test-qdrant-error")

    assert response.status_code == 503
    assert "search service is temporarily unavailable" in response.json()["detail"].lower()
    assert response.json()["error_type"] == "search_service_error"


def test_connection_error_returns_503(client):
    """Test connection error returns 503 with user-friendly message."""
    response = client.get("/test-connection-error")

    assert response.status_code == 503
    assert "unable to connect" in response.json()["detail"].lower()
    assert response.json()["error_type"] == "connection_error"


def test_timeout_error_returns_504(client):
    """Test timeout error returns 504 with user-friendly message."""
    response = client.get("/test-timeout-error")

    assert response.status_code == 504
    assert "took too long" in response.json()["detail"].lower()
    assert response.json()["error_type"] == "timeout_error"


def test_unexpected_error_returns_500(client):
    """Test unexpected error returns 500 with generic message."""
    response = client.get("/test-unexpected-error")

    assert response.status_code == 500
    assert "unexpected error occurred" in response.json()["detail"].lower()
    assert response.json()["error_type"] == "internal_error"


def test_successful_request_passes_through(client):
    """Test successful requests pass through middleware."""
    response = client.get("/test-success")

    assert response.status_code == 200
    assert response.json() == {"message": "success"}


def test_get_user_friendly_error_for_database():
    """Test get_user_friendly_error for database error."""
    error = SQLAlchemyError("Database error")
    result = get_user_friendly_error(error)

    assert "database is temporarily unavailable" in result["detail"].lower()
    assert result["error_type"] == "sqlalchemyerror"


def test_get_user_friendly_error_for_value_error():
    """Test get_user_friendly_error for ValueError."""
    error = ValueError("Invalid value")
    result = get_user_friendly_error(error)

    assert "invalid input" in result["detail"].lower()
    assert result["error_type"] == "valueerror"


def test_get_user_friendly_error_for_unknown_error():
    """Test get_user_friendly_error for unknown error type."""
    error = RuntimeError("Unknown error")
    result = get_user_friendly_error(error)

    assert "unexpected error occurred" in result["detail"].lower()
    assert result["error_type"] == "runtimeerror"


def test_handle_authentication_error():
    """Test authentication error response."""
    response = handle_authentication_error()

    assert response.status_code == 401
    body = response.body.decode()
    assert "session has expired" in body.lower()
    assert "authentication_expired" in body


def test_handle_authorization_error():
    """Test authorization error response."""
    response = handle_authorization_error()

    assert response.status_code == 403
    body = response.body.decode()
    assert "don't have permission" in body.lower()
    assert "authorization_error" in body


def test_handle_not_found_error():
    """Test not found error response."""
    response = handle_not_found_error("Conversation")

    assert response.status_code == 404
    body = response.body.decode()
    assert "conversation not found" in body.lower()
    assert "not_found" in body


def test_handle_validation_error():
    """Test validation error response."""
    response = handle_validation_error("Message content cannot be empty")

    assert response.status_code == 400
    body = response.body.decode()
    assert "message content cannot be empty" in body.lower()
    assert "validation_error" in body
