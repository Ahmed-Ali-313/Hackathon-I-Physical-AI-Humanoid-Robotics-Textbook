"""
Admin API Endpoints
Feature: 005-urdu-translation
Purpose: Administrative endpoints for cache management
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.database import get_db
from src.services.translation_cache_service import TranslationCacheService
from src.api.auth import get_current_user
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize cache service
cache_service = TranslationCacheService()


# Response Models
class CacheInvalidationResponse(BaseModel):
    """Response model for cache invalidation."""
    invalidated: bool
    chapter_id: str
    language_code: str
    message: str


class BulkCacheInvalidationResponse(BaseModel):
    """Response model for bulk cache invalidation."""
    invalidated_count: int
    language_code: str
    message: str


def check_admin_role(current_user: User) -> bool:
    """
    Check if user has admin role.

    Args:
        current_user: Authenticated user

    Returns:
        True if user is admin

    Raises:
        HTTPException: If user is not admin
    """
    # Check if user has admin role (you may need to add is_admin field to User model)
    # For now, we'll check if user email is in admin list
    admin_emails = [
        'admin@example.com',
        # Add more admin emails as needed
    ]

    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Admin access required"
            }
        )

    return True


@router.delete("/cache/{chapter_id}", response_model=CacheInvalidationResponse)
@limiter.limit("20/minute")
async def invalidate_cache(
    chapter_id: str,
    request: Request,
    language_code: str = "ur",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invalidate cached translation for a specific chapter.

    **Authentication Required**: JWT Bearer token with admin role

    **Rate Limit**: 20 requests per minute

    **Args**:
    - chapter_id: Chapter identifier (or "all" to invalidate all chapters)
    - language_code: Language code (default: "ur")

    **Returns**:
    - Invalidation status and message

    **Errors**:
    - 401: Authentication required
    - 403: Admin access required
    - 404: No cache entry found
    """
    # Check admin role
    check_admin_role(current_user)

    logger.info(f"Admin {current_user.email} invalidating cache for {chapter_id}")

    try:
        # Handle bulk invalidation
        if chapter_id == "all":
            count = await cache_service.invalidate_all_caches(db, language_code)

            return BulkCacheInvalidationResponse(
                invalidated_count=count,
                language_code=language_code,
                message=f"Invalidated {count} cached translations"
            )

        # Single chapter invalidation
        deleted = await cache_service.invalidate_cache(
            db=db,
            chapter_id=chapter_id,
            language_code=language_code
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CACHE_NOT_FOUND",
                    "message": f"No cache entry found for {chapter_id}"
                }
            )

        return CacheInvalidationResponse(
            invalidated=True,
            chapter_id=chapter_id,
            language_code=language_code,
            message="Cache invalidated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error invalidating cache for {chapter_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INVALIDATION_ERROR",
                "message": "Error invalidating cache",
                "error": str(e)
            }
        )
