"""
Translation API Endpoints
Feature: 005-urdu-translation
Purpose: REST API for translating textbook chapters to Urdu
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

from src.database import get_db
from src.services.translation_service import TranslationService
from src.services.translation_cache_service import TranslationCacheService
from src.services.validation_service import ValidationService
from src.services.chunking_service import ChunkingService
from src.middleware.auth import get_current_user
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["translation"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize services
translation_service = TranslationService()
cache_service = TranslationCacheService()
validation_service = ValidationService()
chunking_service = ChunkingService()


# Request/Response Models
class TranslateRequest(BaseModel):
    """Request model for translation."""
    chapter_id: str = Field(..., description="Chapter identifier (e.g., '01-introduction-to-ros2')")
    language_code: str = Field(default="ur", description="Target language code")
    force_refresh: bool = Field(default=False, description="Force fresh translation, bypass cache")


class TranslateResponse(BaseModel):
    """Response model for translation."""
    chapter_id: str
    language_code: str
    translated_content: str
    cached: bool
    translated_at: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: dict


@router.post("/translate", response_model=TranslateResponse)
@limiter.limit("10/minute")
async def translate_chapter(
    translate_request: TranslateRequest,
    request: Request,
    current_user: str = Depends(get_current_user),  # Fixed: returns str, not User
    db: AsyncSession = Depends(get_db)
):
    """
    Translate a textbook chapter from English to Urdu.

    **Authentication Required**: JWT Bearer token

    **Rate Limit**: 10 requests per minute per user

    **Process**:
    1. Validate chapter_id and language_code
    2. Load chapter content from markdown file
    3. Check cache (if not force_refresh)
    4. If cache miss, translate using OpenAI API
    5. Validate translation
    6. Save to cache
    7. Return translated content

    **Args**:
    - chapter_id: Slug-based chapter identifier (e.g., "01-introduction-to-ros2")
    - language_code: Target language ("ur" for Urdu)
    - force_refresh: If true, bypass cache and request fresh translation

    **Returns**:
    - Translated markdown content with metadata

    **Errors**:
    - 400: Invalid chapter_id or language_code
    - 401: Authentication required
    - 404: Chapter not found
    - 429: Rate limit exceeded
    - 500: Translation service error
    """
    try:
        # Validate inputs
        if not validation_service.validate_chapter_id(translate_request.chapter_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CHAPTER_ID",
                    "message": f"Invalid chapter identifier format: {translate_request.chapter_id}",
                    "expected_format": "alphanumeric with hyphens and slashes (e.g., 'intro', 'module-1-ros2/urdf-humanoids')"
                }
            )

        if not validation_service.validate_language_code(translate_request.language_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_LANGUAGE",
                    "message": f"Unsupported language code: {translate_request.language_code}",
                    "supported_languages": ["ur"]
                }
            )

        logger.info(f"Translation request from user {current_user} for {translate_request.chapter_id}")

        # Load chapter content from file
        chapter_content = await _load_chapter_content(translate_request.chapter_id)
        if not chapter_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CHAPTER_NOT_FOUND",
                    "message": f"Chapter not found: {translate_request.chapter_id}"
                }
            )

        # Compute content hash for cache invalidation
        content_hash = validation_service.compute_content_hash(chapter_content)

        # Check cache (unless force_refresh)
        cached_translation = None
        if not translate_request.force_refresh:
            cached_translation = await cache_service.get_cached_translation(
                db=db,
                chapter_id=translate_request.chapter_id,
                language_code=translate_request.language_code,
                current_content_hash=content_hash
            )

        if cached_translation:
            # Return cached translation
            logger.info(f"Returning cached translation for {translate_request.chapter_id}")
            return TranslateResponse(
                chapter_id=cached_translation.chapter_id,
                language_code=cached_translation.language_code,
                translated_content=cached_translation.translated_content,
                cached=True,
                translated_at=cached_translation.updated_at.isoformat()
            )

        # Cache miss - perform translation
        logger.info(f"Cache miss for {translate_request.chapter_id}, translating...")

        # Check if chapter needs chunking
        if chunking_service.should_chunk(chapter_content):
            # Chunk and translate
            chunks = chunking_service.chunk_by_headers(chapter_content)
            logger.info(f"Chunking {translate_request.chapter_id} into {len(chunks)} sections")

            translated_content = await translation_service.translate_chunked(
                chapter_id=translate_request.chapter_id,
                chunks=chunks,
                language_code=translate_request.language_code,
                chapter_title=_extract_title(chapter_content)
            )
        else:
            # Translate whole chapter
            translated_content = await translation_service.translate(
                chapter_id=translate_request.chapter_id,
                content=chapter_content,
                language_code=translate_request.language_code,
                user_level=None,  # Fixed: current_user is str (user_id), not User object
                chapter_title=_extract_title(chapter_content)
            )

        # Save to cache
        saved_translation = await cache_service.save_translation(
            db=db,
            chapter_id=translate_request.chapter_id,
            language_code=translate_request.language_code,
            translated_content=translated_content,
            original_hash=content_hash
        )

        logger.info(f"Translation completed and cached for {translate_request.chapter_id}")

        return TranslateResponse(
            chapter_id=saved_translation.chapter_id,
            language_code=saved_translation.language_code,
            translated_content=saved_translation.translated_content,
            cached=False,
            translated_at=saved_translation.created_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error for {translate_request.chapter_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "TRANSLATION_FAILED",
                "message": "Translation service error. Please try again later.",
                "error": str(e)
            }
        )


@router.get("/translate/{chapter_id:path}", response_model=TranslateResponse)
async def get_cached_translation(
    chapter_id: str,
    language_code: str = "ur",
    current_user: str = Depends(get_current_user),  # Fixed: returns str, not User
    db: AsyncSession = Depends(get_db)
):
    """
    Get cached translation for a chapter.

    **Authentication Required**: JWT Bearer token

    **Args**:
    - chapter_id: Chapter identifier
    - language_code: Language code (default: "ur")

    **Returns**:
    - Cached translation if available

    **Errors**:
    - 401: Authentication required
    - 404: Translation not found in cache
    """
    try:
        # Load chapter content to compute hash
        chapter_content = await _load_chapter_content(chapter_id)
        if not chapter_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CHAPTER_NOT_FOUND",
                    "message": f"Chapter not found: {chapter_id}"
                }
            )

        content_hash = validation_service.compute_content_hash(chapter_content)

        # Get cached translation
        cached_translation = await cache_service.get_cached_translation(
            db=db,
            chapter_id=chapter_id,
            language_code=language_code,
            current_content_hash=content_hash
        )

        if not cached_translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "TRANSLATION_NOT_FOUND",
                    "message": f"No cached translation found for {chapter_id}"
                }
            )

        return TranslateResponse(
            chapter_id=cached_translation.chapter_id,
            language_code=cached_translation.language_code,
            translated_content=cached_translation.translated_content,
            cached=True,
            translated_at=cached_translation.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cached translation for {chapter_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "CACHE_ERROR",
                "message": "Error retrieving cached translation",
                "error": str(e)
            }
        )


# Helper functions
async def _load_chapter_content(chapter_id: str) -> Optional[str]:
    """
    Load chapter content from markdown file.

    Args:
        chapter_id: Chapter identifier (e.g., "intro", "module-1-ros2/urdf-humanoids")

    Returns:
        Chapter markdown content or None if not found
    """
    try:
        # Construct file path - chapter_id may include subdirectories
        textbook_dir = os.path.join(os.path.dirname(__file__), "../../../textbook/docs")
        file_path = os.path.join(textbook_dir, f"{chapter_id}.md")

        # Normalize path to prevent directory traversal attacks
        file_path = os.path.normpath(file_path)
        textbook_dir = os.path.normpath(textbook_dir)

        # Security check: ensure file is within textbook/docs directory
        if not file_path.startswith(textbook_dir):
            logger.warning(f"Invalid chapter path (security): {chapter_id}")
            return None

        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"Successfully loaded chapter: {chapter_id}")
        return content

    except FileNotFoundError:
        logger.warning(f"Chapter file not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading chapter {chapter_id}: {str(e)}")
        return None


def _extract_title(content: str) -> str:
    """Extract chapter title from markdown (first # header)."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Chapter"


def _get_user_level(user: User) -> Optional[str]:
    """
    Get user's technical background level from profile.

    Args:
        user: User model

    Returns:
        User level ('beginner', 'intermediate', 'advanced') or None
    """
    # Check if user has personalization profile with background level
    if hasattr(user, 'personalization_profile') and user.personalization_profile:
        profile = user.personalization_profile
        if hasattr(profile, 'ros2_level'):
            return profile.ros2_level

    return None
