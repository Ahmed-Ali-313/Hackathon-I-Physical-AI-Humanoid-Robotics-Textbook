"""
Integration Tests for User Preferences API (Translation Feature)
Tasks: T044, T045
Feature: 005-urdu-translation
Purpose: Test preference persistence for language selection
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from src.main import app


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user."""
    from unittest.mock import MagicMock
    user = MagicMock()
    user.id = "test-user-123"
    user.email = "test@example.com"
    return user


def setup_auth_override(user=None):
    """Helper to setup authentication override."""
    from src.middleware.auth import get_current_user
    from src.database import get_db

    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    if user:
        app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = override_get_db

    return mock_db


def clear_overrides():
    """Helper to clear dependency overrides."""
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_user_language_preference_success(mock_auth_user):
    """Test T044: PUT /api/v1/user/preferences to update language preference."""
    from unittest.mock import patch, MagicMock, AsyncMock

    async with AsyncClient(app=app, base_url="http://test") as client:
        setup_auth_override(mock_auth_user)

        try:
            # Mock the preference service
            mock_profile = MagicMock()
            mock_profile.id = "profile-123"
            mock_profile.user_id = mock_auth_user.id
            mock_profile.preferred_language = "ur"
            mock_profile.workstation_type = "laptop"
            mock_profile.is_personalized = True
            mock_profile.created_at = MagicMock()
            mock_profile.updated_at = MagicMock()
            mock_profile.created_at.isoformat.return_value = "2026-03-01T10:00:00"
            mock_profile.updated_at.isoformat.return_value = "2026-03-01T10:00:00"

            # Use AsyncMock that returns the profile
            async_mock = AsyncMock(return_value=mock_profile)

            with patch('src.services.preference_service.update_preferences', new=async_mock):
                # Act
                response = await client.put(
                    "/api/v1/preferences",
                    json={"preferred_language": "ur"},
                    headers={"Authorization": "Bearer test-token"}
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["preferred_language"] == "ur"
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_update_user_language_preference_invalid_language(mock_auth_user):
    """Test T044: PUT /api/v1/user/preferences with invalid language code."""
    from unittest.mock import patch, AsyncMock

    async with AsyncClient(app=app, base_url="http://test") as client:
        setup_auth_override(mock_auth_user)

        try:
            async_mock = AsyncMock(side_effect=ValueError("Invalid language"))

            with patch('src.services.preference_service.update_preferences', new=async_mock):
                # Act
                response = await client.put(
                    "/api/v1/preferences",
                    json={"preferred_language": "invalid"},
                    headers={"Authorization": "Bearer test-token"}
                )

                # Assert - Should handle validation error
                assert response.status_code in [400, 422, 500]
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_get_user_preferences_success(mock_auth_user):
    """Test T045: GET /api/v1/user/preferences to retrieve language preference."""
    from unittest.mock import patch, MagicMock, AsyncMock

    async with AsyncClient(app=app, base_url="http://test") as client:
        setup_auth_override(mock_auth_user)

        try:
            # Mock the preference service
            mock_profile = MagicMock()
            mock_profile.id = "profile-123"
            mock_profile.user_id = mock_auth_user.id
            mock_profile.preferred_language = "ur"
            mock_profile.workstation_type = "laptop"
            mock_profile.ros2_level = "intermediate"
            mock_profile.is_personalized = True
            mock_profile.created_at = MagicMock()
            mock_profile.updated_at = MagicMock()
            mock_profile.created_at.isoformat.return_value = "2026-03-01T10:00:00"
            mock_profile.updated_at.isoformat.return_value = "2026-03-01T10:00:00"

            async_mock = AsyncMock(return_value=mock_profile)

            with patch('src.services.preference_service.get_preferences', new=async_mock):
                # Act
                response = await client.get(
                    "/api/v1/preferences",
                    headers={"Authorization": "Bearer test-token"}
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["preferred_language"] == "ur"
                assert data["user_id"] == mock_auth_user.id
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_get_user_preferences_not_found(mock_auth_user):
    """Test T045: GET /api/v1/user/preferences when no preferences exist."""
    from unittest.mock import patch, AsyncMock

    async with AsyncClient(app=app, base_url="http://test") as client:
        setup_auth_override(mock_auth_user)

        try:
            async_mock = AsyncMock(return_value=None)

            with patch('src.services.preference_service.get_preferences', new=async_mock):
                # Act
                response = await client.get(
                    "/api/v1/preferences",
                    headers={"Authorization": "Bearer test-token"}
                )

                # Assert
                assert response.status_code == 404
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_get_user_preferences_unauthenticated():
    """Test T045: GET /api/v1/user/preferences without authentication."""
    clear_overrides()

    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            # Act
            response = await client.get("/api/v1/preferences")

            # Assert - Accept both 401 and 403 as valid auth failures
            assert response.status_code in [401, 403]
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_update_user_preferences_unauthenticated():
    """Test T044: PUT /api/v1/user/preferences without authentication."""
    clear_overrides()

    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            # Act
            response = await client.put(
                "/api/v1/preferences",
                json={"preferred_language": "ur"}
            )

            # Assert - Accept both 401 and 403 as valid auth failures
            assert response.status_code in [401, 403]
        finally:
            clear_overrides()


@pytest.mark.asyncio
async def test_language_preference_toggle_workflow(mock_auth_user):
    """Test complete workflow: get preferences, update to Urdu, get again."""
    from unittest.mock import patch, MagicMock, AsyncMock

    async with AsyncClient(app=app, base_url="http://test") as client:
        setup_auth_override(mock_auth_user)

        try:
            # Step 1: Get initial preferences (English)
            mock_profile_en = MagicMock()
            mock_profile_en.preferred_language = "en"
            mock_profile_en.user_id = mock_auth_user.id
            mock_profile_en.created_at = MagicMock()
            mock_profile_en.updated_at = MagicMock()
            mock_profile_en.created_at.isoformat.return_value = "2026-03-01T10:00:00"
            mock_profile_en.updated_at.isoformat.return_value = "2026-03-01T10:00:00"

            async_mock_get = AsyncMock(return_value=mock_profile_en)

            with patch('src.services.preference_service.get_preferences', new=async_mock_get):
                response = await client.get(
                    "/api/v1/preferences",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
                assert response.json()["preferred_language"] == "en"

            # Step 2: Update to Urdu
            mock_profile_ur = MagicMock()
            mock_profile_ur.preferred_language = "ur"
            mock_profile_ur.user_id = mock_auth_user.id
            mock_profile_ur.created_at = MagicMock()
            mock_profile_ur.updated_at = MagicMock()
            mock_profile_ur.created_at.isoformat.return_value = "2026-03-01T10:00:00"
            mock_profile_ur.updated_at.isoformat.return_value = "2026-03-01T10:01:00"

            async_mock_update = AsyncMock(return_value=mock_profile_ur)

            with patch('src.services.preference_service.update_preferences', new=async_mock_update):
                response = await client.put(
                    "/api/v1/preferences",
                    json={"preferred_language": "ur"},
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
                assert response.json()["preferred_language"] == "ur"

            # Step 3: Get preferences again (should be Urdu)
            async_mock_get2 = AsyncMock(return_value=mock_profile_ur)

            with patch('src.services.preference_service.get_preferences', new=async_mock_get2):
                response = await client.get(
                    "/api/v1/preferences",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
                assert response.json()["preferred_language"] == "ur"
        finally:
            clear_overrides()
