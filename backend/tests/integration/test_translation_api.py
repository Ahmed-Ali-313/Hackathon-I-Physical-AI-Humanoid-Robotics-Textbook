"""
Integration Tests for Translation API
Feature: 005-urdu-translation
Purpose: Test translation API endpoints with database integration
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import app


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = "test-user-123"
    user.email = "test@example.com"
    return user


@pytest.mark.asyncio
async def test_translate_chapter_success(mock_auth_user):
    """Test successful chapter translation (T018)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Mock chapter file loading
            with patch('src.api.translation._load_chapter_content', return_value="# Test Chapter\n\nROS 2 content"):
                # Mock OpenAI API
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "# ٹیسٹ باب\n\nROS 2 مواد"

                with patch('src.services.translation_service.AsyncOpenAI') as mock_openai:
                    mock_client = AsyncMock()
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_openai.return_value = mock_client

                    # Act
                    response = await client.post(
                        "/api/v1/translate",
                        json={
                            "chapter_id": "01-test-chapter",
                            "language_code": "ur"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Assert
                    assert response.status_code == 200
                    data = response.json()
                    assert data["chapter_id"] == "01-test-chapter"
                    assert data["language_code"] == "ur"
                    assert "translated_content" in data
                    assert data["cached"] is False


@pytest.mark.asyncio
async def test_translate_chapter_unauthenticated():
    """Test translation requires authentication (T039)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.post(
            "/api/v1/translate",
            json={
                "chapter_id": "01-test-chapter",
                "language_code": "ur"
            }
        )

        # Assert
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_translate_chapter_invalid_chapter_id(mock_auth_user):
    """Test translation with invalid chapter ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Act
            response = await client.post(
                "/api/v1/translate",
                json={
                    "chapter_id": "invalid-format",
                    "language_code": "ur"
                },
                headers={"Authorization": "Bearer test-token"}
            )

            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "INVALID_CHAPTER_ID" in str(data)


@pytest.mark.asyncio
async def test_translate_chapter_not_found(mock_auth_user):
    """Test translation with non-existent chapter."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Mock chapter not found
            with patch('src.api.translation._load_chapter_content', return_value=None):
                # Act
                response = await client.post(
                    "/api/v1/translate",
                    json={
                        "chapter_id": "99-nonexistent",
                        "language_code": "ur"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Assert
                assert response.status_code == 404


@pytest.mark.asyncio
async def test_translate_chapter_cached(mock_auth_user):
    """Test cached translation retrieval (T061)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Mock chapter file
            with patch('src.api.translation._load_chapter_content', return_value="# Test"):
                # Mock cached translation exists
                mock_cached = MagicMock()
                mock_cached.chapter_id = "01-test"
                mock_cached.language_code = "ur"
                mock_cached.translated_content = "# ٹیسٹ"
                mock_cached.updated_at = MagicMock()
                mock_cached.updated_at.isoformat.return_value = "2026-02-28T10:00:00"

                with patch('src.services.translation_cache_service.TranslationCacheService.get_cached_translation', return_value=mock_cached):
                    # Act
                    response = await client.post(
                        "/api/v1/translate",
                        json={
                            "chapter_id": "01-test",
                            "language_code": "ur"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Assert
                    assert response.status_code == 200
                    data = response.json()
                    assert data["cached"] is True
                    assert data["translated_content"] == "# ٹیسٹ"


@pytest.mark.asyncio
async def test_get_cached_translation_success(mock_auth_user):
    """Test GET endpoint for cached translation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Mock chapter file
            with patch('src.api.translation._load_chapter_content', return_value="# Test"):
                # Mock cached translation
                mock_cached = MagicMock()
                mock_cached.chapter_id = "01-test"
                mock_cached.language_code = "ur"
                mock_cached.translated_content = "# ٹیسٹ"
                mock_cached.updated_at = MagicMock()
                mock_cached.updated_at.isoformat.return_value = "2026-02-28T10:00:00"

                with patch('src.services.translation_cache_service.TranslationCacheService.get_cached_translation', return_value=mock_cached):
                    # Act
                    response = await client.get(
                        "/api/v1/translate/01-test?language_code=ur",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Assert
                    assert response.status_code == 200
                    data = response.json()
                    assert data["chapter_id"] == "01-test"
                    assert data["cached"] is True


@pytest.mark.asyncio
async def test_get_cached_translation_not_found(mock_auth_user):
    """Test GET endpoint when cache doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch('src.middleware.auth.get_current_user', return_value=mock_auth_user):
            # Mock chapter file
            with patch('src.api.translation._load_chapter_content', return_value="# Test"):
                # Mock no cached translation
                with patch('src.services.translation_cache_service.TranslationCacheService.get_cached_translation', return_value=None):
                    # Act
                    response = await client.get(
                        "/api/v1/translate/01-test?language_code=ur",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Assert
                    assert response.status_code == 404


@pytest.mark.asyncio
async def test_translate_chapter_rate_limit():
    """Test rate limiting on translation endpoint."""
    # This test would require actual rate limiter setup
    # Placeholder for rate limit testing
    pass


@pytest.mark.asyncio
async def test_admin_invalidate_cache_success():
    """Test admin cache invalidation (T082)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock admin user
        admin_user = MagicMock()
        admin_user.id = "admin-123"
        admin_user.email = "admin@example.com"

        with patch('src.middleware.auth.get_current_user', return_value=admin_user):
            with patch('src.services.translation_cache_service.TranslationCacheService.invalidate_cache', return_value=True):
                # Act
                response = await client.delete(
                    "/api/v1/admin/cache/01-test?language_code=ur",
                    headers={"Authorization": "Bearer admin-token"}
                )

                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["invalidated"] is True


@pytest.mark.asyncio
async def test_admin_invalidate_cache_forbidden():
    """Test non-admin cannot invalidate cache (T083)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock regular user
        user = MagicMock()
        user.id = "user-123"
        user.email = "user@example.com"

        with patch('src.middleware.auth.get_current_user', return_value=user):
            # Act
            response = await client.delete(
                "/api/v1/admin/cache/01-test?language_code=ur",
                headers={"Authorization": "Bearer user-token"}
            )

            # Assert
            assert response.status_code == 403
