"""
Content API Router

Endpoints for content metadata and recommendations.

Endpoints:
- GET /api/v1/content/metadata - Get all content metadata
- GET /api/v1/content/recommendations - Get recommended content for user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.database import get_db
from src.middleware.auth import get_current_user
from src.models.content_metadata import ContentMetadata
from src.services.preference_service import get_preferences
from src.services.matching_service import is_recommended


router = APIRouter()


# Pydantic schemas
class ContentMetadataResponse(BaseModel):
    """Response schema for content metadata"""
    id: str
    content_id: str
    content_path: str
    title: str
    hardware_tags: Optional[List[str]]
    software_requirements: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecommendationsResponse(BaseModel):
    """Response schema for recommendations"""
    recommended_content_ids: List[str]


@router.get(
    "/content/metadata",
    response_model=List[ContentMetadataResponse],
    summary="Get all content metadata",
    description="Retrieve metadata for all content items"
)
async def get_content_metadata(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all content metadata.

    Returns:
        List of content metadata

    Note: This endpoint is public (no authentication required)
    """
    result = await db.execute(select(ContentMetadata))
    metadata_list = result.scalars().all()

    return [ContentMetadataResponse.model_validate(m) for m in metadata_list]


@router.get(
    "/content/recommendations",
    response_model=RecommendationsResponse,
    summary="Get recommended content",
    description="Get list of content IDs recommended for authenticated user based on preferences"
)
async def get_recommendations(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended content for authenticated user.

    Args:
        user_id: Authenticated user ID (from JWT)
        db: Database session

    Returns:
        List of recommended content IDs

    Raises:
        404: User has no preferences
    """
    # Get user preferences
    profile = await get_preferences(db, user_id=user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    # If user is not personalized, return empty list
    if not profile.is_personalized:
        return RecommendationsResponse(recommended_content_ids=[])

    # Get all content metadata
    result = await db.execute(select(ContentMetadata))
    all_content = result.scalars().all()

    # Convert user preferences to dict
    user_prefs = {
        "workstation_type": profile.workstation_type,
        "edge_kit_available": profile.edge_kit_available,
        "robot_tier_access": profile.robot_tier_access,
        "ros2_level": profile.ros2_level,
        "gazebo_level": profile.gazebo_level,
        "unity_level": profile.unity_level,
        "isaac_level": profile.isaac_level,
        "vla_level": profile.vla_level,
    }

    # Filter recommended content
    recommended_ids = []
    for content in all_content:
        content_meta = {
            "hardware_tags": content.hardware_tags or [],
            "software_requirements": content.software_requirements or {}
        }

        if is_recommended(user_prefs, content_meta):
            recommended_ids.append(content.content_id)

    return RecommendationsResponse(recommended_content_ids=recommended_ids)
