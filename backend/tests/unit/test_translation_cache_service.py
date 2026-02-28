"""
Unit Tests for TranslationCacheService
Feature: 005-urdu-translation
Purpose: Test caching logic, optimistic locking, and invalidation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from src.services.translation_cache_service import TranslationCacheService
from src.models.translated_chapter import TranslatedChapter


@pytest.fixture
def cache_service():
    """Create TranslationCacheService instance for testing."""
    return TranslationCacheService(cache_expiry_days=30)


@pytest.mark.asyncio
async def test_get_cached_translation_success(cache_service):
    """Test successful cache retrieval (T056)."""
    # Arrange
    mock_db = AsyncMock()
    chapter_id = "01-test-chapter"
    language_code = "ur"
    current_hash = "abc123"

    # Mock cached translation
    cached = TranslatedChapter(
        chapter_id=chapter_id,
        language_code=language_code,
        translated_content="مترجم مواد",
        original_hash=current_hash,
        version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = cached
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.get_cached_translation(
        db=mock_db,
        chapter_id=chapter_id,
        language_code=language_code,
        current_content_hash=current_hash
    )

    # Assert
    assert result is not None
    assert result.chapter_id == chapter_id
    assert result.translated_content == "مترجم مواد"


@pytest.mark.asyncio
async def test_get_cached_translation_not_found(cache_service):
    """Test cache miss when translation doesn't exist."""
    # Arrange
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.get_cached_translation(
        db=mock_db,
        chapter_id="01-test",
        language_code="ur",
        current_content_hash="abc123"
    )

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_cached_translation_hash_mismatch(cache_service):
    """Test cache invalidation on hash mismatch (T059)."""
    # Arrange
    mock_db = AsyncMock()
    chapter_id = "01-test-chapter"

    # Mock cached translation with old hash
    cached = TranslatedChapter(
        chapter_id=chapter_id,
        language_code="ur",
        translated_content="مترجم مواد",
        original_hash="old_hash",
        version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = cached
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.get_cached_translation(
        db=mock_db,
        chapter_id=chapter_id,
        language_code="ur",
        current_content_hash="new_hash"  # Different hash!
    )

    # Assert
    assert result is None, "Should return None when hash doesn't match"
    # Verify invalidate was called
    assert mock_db.execute.call_count >= 2, "Should call execute for query and delete"


@pytest.mark.asyncio
async def test_get_cached_translation_expired(cache_service):
    """Test cache expiration after 30 days (T060)."""
    # Arrange
    mock_db = AsyncMock()
    chapter_id = "01-test-chapter"

    # Mock cached translation that's 31 days old
    old_date = datetime.utcnow() - timedelta(days=31)
    cached = TranslatedChapter(
        chapter_id=chapter_id,
        language_code="ur",
        translated_content="مترجم مواد",
        original_hash="abc123",
        version=1,
        created_at=old_date,
        updated_at=old_date
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = cached
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.get_cached_translation(
        db=mock_db,
        chapter_id=chapter_id,
        language_code="ur",
        current_content_hash="abc123"
    )

    # Assert
    assert result is None, "Should return None for expired cache"


@pytest.mark.asyncio
async def test_save_translation_new(cache_service):
    """Test saving new translation (T057)."""
    # Arrange
    mock_db = AsyncMock()
    chapter_id = "01-test-chapter"
    translated_content = "مترجم مواد"
    original_hash = "abc123"

    # Mock no existing translation
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.save_translation(
        db=mock_db,
        chapter_id=chapter_id,
        language_code="ur",
        translated_content=translated_content,
        original_hash=original_hash
    )

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_save_translation_update_existing(cache_service):
    """Test updating existing translation with version increment (T058)."""
    # Arrange
    mock_db = AsyncMock()
    chapter_id = "01-test-chapter"

    # Mock existing translation
    existing = TranslatedChapter(
        chapter_id=chapter_id,
        language_code="ur",
        translated_content="old content",
        original_hash="old_hash",
        version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.save_translation(
        db=mock_db,
        chapter_id=chapter_id,
        language_code="ur",
        translated_content="new content",
        original_hash="new_hash"
    )

    # Assert
    assert existing.version == 2, "Version should be incremented"
    assert existing.translated_content == "new content"
    assert existing.original_hash == "new_hash"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_invalidate_cache_success(cache_service):
    """Test cache invalidation."""
    # Arrange
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.invalidate_cache(
        db=mock_db,
        chapter_id="01-test",
        language_code="ur"
    )

    # Assert
    assert result is True
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_invalidate_cache_not_found(cache_service):
    """Test cache invalidation when entry doesn't exist."""
    # Arrange
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_db.execute.return_value = mock_result

    # Act
    result = await cache_service.invalidate_cache(
        db=mock_db,
        chapter_id="01-test",
        language_code="ur"
    )

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_invalidate_all_caches(cache_service):
    """Test bulk cache invalidation."""
    # Arrange
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.rowcount = 5  # 5 caches deleted
    mock_db.execute.return_value = mock_result

    # Act
    count = await cache_service.invalidate_all_caches(
        db=mock_db,
        language_code="ur"
    )

    # Assert
    assert count == 5
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_cache_expiry_custom_days(cache_service):
    """Test custom cache expiry period."""
    # Arrange
    custom_service = TranslationCacheService(cache_expiry_days=7)
    assert custom_service.cache_expiry_days == 7

    mock_db = AsyncMock()

    # Mock cached translation that's 8 days old
    old_date = datetime.utcnow() - timedelta(days=8)
    cached = TranslatedChapter(
        chapter_id="01-test",
        language_code="ur",
        translated_content="content",
        original_hash="abc123",
        version=1,
        created_at=old_date,
        updated_at=old_date
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = cached
    mock_db.execute.return_value = mock_result

    # Act
    result = await custom_service.get_cached_translation(
        db=mock_db,
        chapter_id="01-test",
        language_code="ur",
        current_content_hash="abc123"
    )

    # Assert
    assert result is None, "Should expire after 7 days with custom setting"
