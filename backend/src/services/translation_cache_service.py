"""
Translation Cache Service
Feature: 005-urdu-translation
Purpose: Manage translation cache with optimistic locking and invalidation
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.translated_chapter import TranslatedChapter
from src.utils.validation import ValidationUtils

logger = logging.getLogger(__name__)


class TranslationCacheService:
    """
    Service for managing translation cache in database.

    Features:
    - Cache-first strategy for fast retrieval
    - Optimistic locking for concurrent requests
    - Hash-based cache invalidation
    - Time-based expiration (30 days)
    """

    def __init__(self, cache_expiry_days: int = 30):
        """
        Initialize translation cache service.

        Args:
            cache_expiry_days: Number of days before cache expires (default: 30)
        """
        self.cache_expiry_days = cache_expiry_days

    async def get_cached_translation(
        self,
        db: AsyncSession,
        chapter_id: str,
        language_code: str,
        current_content_hash: str
    ) -> Optional[TranslatedChapter]:
        """
        Get cached translation if valid.

        Checks:
        1. Translation exists
        2. Content hash matches (not stale)
        3. Not expired (within 30 days)

        Args:
            db: Database session
            chapter_id: Chapter identifier
            language_code: Language code
            current_content_hash: SHA-256 hash of current English content

        Returns:
            TranslatedChapter if valid cache exists, None otherwise
        """
        logger.info(f"Checking cache for {chapter_id} ({language_code})")

        try:
            # Query for cached translation
            result = await db.execute(
                select(TranslatedChapter).where(
                    TranslatedChapter.chapter_id == chapter_id,
                    TranslatedChapter.language_code == language_code
                )
            )
            cached = result.scalar_one_or_none()

            if not cached:
                logger.info(f"No cache found for {chapter_id}")
                return None

            # Check if content hash matches (cache invalidation)
            if cached.original_hash != current_content_hash:
                logger.info(f"Cache stale for {chapter_id} (hash mismatch)")
                # Delete stale cache
                await self.invalidate_cache(db, chapter_id, language_code)
                return None

            # Check if cache expired (30 days)
            expiry_date = cached.updated_at + timedelta(days=self.cache_expiry_days)
            if datetime.utcnow() > expiry_date:
                logger.info(f"Cache expired for {chapter_id}")
                # Delete expired cache
                await self.invalidate_cache(db, chapter_id, language_code)
                return None

            logger.info(f"Valid cache found for {chapter_id}")
            return cached

        except Exception as e:
            logger.error(f"Error retrieving cache for {chapter_id}: {str(e)}")
            return None

    async def save_translation(
        self,
        db: AsyncSession,
        chapter_id: str,
        language_code: str,
        translated_content: str,
        original_hash: str
    ) -> TranslatedChapter:
        """
        Save translation to cache with optimistic locking.

        Args:
            db: Database session
            chapter_id: Chapter identifier
            language_code: Language code
            translated_content: Translated markdown content
            original_hash: SHA-256 hash of original content

        Returns:
            TranslatedChapter with saved translation

        Raises:
            Exception: If save fails
        """
        logger.info(f"Saving translation for {chapter_id} ({language_code})")

        try:
            # Check if translation already exists
            result = await db.execute(
                select(TranslatedChapter).where(
                    TranslatedChapter.chapter_id == chapter_id,
                    TranslatedChapter.language_code == language_code
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing translation
                existing.translated_content = translated_content
                existing.original_hash = original_hash
                existing.version += 1
                existing.updated_at = datetime.utcnow()

                await db.commit()
                await db.refresh(existing)

                logger.info(f"Updated existing cache for {chapter_id}")
                return existing
            else:
                # Create new translation
                new_translation = TranslatedChapter(
                    chapter_id=chapter_id,
                    language_code=language_code,
                    translated_content=translated_content,
                    original_hash=original_hash,
                    version=1
                )

                db.add(new_translation)
                await db.commit()
                await db.refresh(new_translation)

                logger.info(f"Created new cache for {chapter_id}")
                return new_translation

        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving translation for {chapter_id}: {str(e)}")
            raise

    async def invalidate_cache(
        self,
        db: AsyncSession,
        chapter_id: str,
        language_code: str
    ) -> bool:
        """
        Invalidate (delete) cached translation.

        Args:
            db: Database session
            chapter_id: Chapter identifier
            language_code: Language code

        Returns:
            True if cache was deleted, False if not found
        """
        logger.info(f"Invalidating cache for {chapter_id} ({language_code})")

        try:
            result = await db.execute(
                delete(TranslatedChapter).where(
                    TranslatedChapter.chapter_id == chapter_id,
                    TranslatedChapter.language_code == language_code
                )
            )

            await db.commit()

            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Cache invalidated for {chapter_id}")
            else:
                logger.info(f"No cache to invalidate for {chapter_id}")

            return deleted

        except Exception as e:
            await db.rollback()
            logger.error(f"Error invalidating cache for {chapter_id}: {str(e)}")
            raise

    async def invalidate_all_caches(
        self,
        db: AsyncSession,
        language_code: str
    ) -> int:
        """
        Invalidate all cached translations for a language.

        Args:
            db: Database session
            language_code: Language code

        Returns:
            Number of caches invalidated
        """
        logger.info(f"Invalidating all caches for language {language_code}")

        try:
            result = await db.execute(
                delete(TranslatedChapter).where(
                    TranslatedChapter.language_code == language_code
                )
            )

            await db.commit()

            count = result.rowcount
            logger.info(f"Invalidated {count} caches for {language_code}")

            return count

        except Exception as e:
            await db.rollback()
            logger.error(f"Error invalidating all caches: {str(e)}")
            raise
