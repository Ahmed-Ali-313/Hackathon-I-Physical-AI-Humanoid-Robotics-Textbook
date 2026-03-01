"""
Preferences API Router

Endpoints for managing user personalization preferences.

Endpoints:
- POST /api/v1/preferences - Create preferences
- GET /api/v1/preferences - Get user preferences
- PUT /api/v1/preferences - Update preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from src.database import get_db
from src.middleware.auth import get_current_user
from src.services.preference_service import (
    create_preferences,
    get_preferences,
    update_preferences,
    clear_preferences,
    get_preference_history
)


router = APIRouter()


# Pydantic schemas
class PreferenceInput(BaseModel):
    """Input schema for creating/updating preferences"""
    workstation_type: Optional[str] = Field(None, description="Type of workstation")
    edge_kit_available: Optional[str] = Field(None, description="Available edge computing kit (none, jetson_nano, jetson_orin, raspberry_pi)")
    robot_tier_access: Optional[str] = Field(None, description="Robot hardware tier access")
    ros2_level: Optional[str] = Field(None, description="ROS2 experience level")
    gazebo_level: Optional[str] = Field(None, description="Gazebo experience level")
    unity_level: Optional[str] = Field(None, description="Unity experience level")
    isaac_level: Optional[str] = Field(None, description="Isaac Sim experience level")
    vla_level: Optional[str] = Field(None, description="VLA experience level")
    preferred_language: Optional[str] = Field(None, description="Preferred language for textbook content (en or ur)")


class PreferenceResponse(BaseModel):
    """Response schema for preferences"""
    id: UUID
    user_id: UUID
    workstation_type: Optional[str]
    edge_kit_available: Optional[str]
    robot_tier_access: Optional[str]
    ros2_level: Optional[str]
    gazebo_level: Optional[str]
    unity_level: Optional[str]
    isaac_level: Optional[str]
    vla_level: Optional[str]
    preferred_language: Optional[str]
    is_personalized: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post(
    "/preferences",
    response_model=PreferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user preferences",
    description="Create personalization preferences for the authenticated user"
)
async def create_user_preferences(
    preferences: PreferenceInput,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create personalization preferences for authenticated user.

    Args:
        preferences: Preference data
        user_id: Authenticated user ID (from JWT)
        db: Database session

    Returns:
        Created preferences

    Raises:
        409: User already has preferences
        422: Invalid enum values
    """
    from src.models.user import User

    try:
        profile = await create_preferences(
            db,
            user_id=user_id,
            preferences=preferences.model_dump(exclude_unset=True)
        )

        # Get user's preferred_language from users table
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        # Build response with preferred_language from user
        response_data = {
            "id": profile.id,
            "user_id": profile.user_id,
            "workstation_type": profile.workstation_type,
            "edge_kit_available": profile.edge_kit_available,
            "robot_tier_access": profile.robot_tier_access,
            "ros2_level": profile.ros2_level,
            "gazebo_level": profile.gazebo_level,
            "unity_level": profile.unity_level,
            "isaac_level": profile.isaac_level,
            "vla_level": profile.vla_level,
            "preferred_language": user.preferred_language if user else 'en',
            "is_personalized": profile.is_personalized,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }

        return PreferenceResponse.model_validate(response_data)

    except ValueError as e:
        if "already has preferences" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )


@router.get(
    "/preferences",
    response_model=PreferenceResponse,
    summary="Get user preferences",
    description="Retrieve personalization preferences for the authenticated user"
)
async def get_user_preferences(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalization preferences for authenticated user.

    Args:
        user_id: Authenticated user ID (from JWT)
        db: Database session

    Returns:
        User preferences

    Raises:
        404: User has no preferences
    """
    from src.models.user import User

    profile = await get_preferences(db, user_id=user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found for this user"
        )

    # Get user's preferred_language from users table
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()

    # Build response with preferred_language from user
    response_data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "workstation_type": profile.workstation_type,
        "edge_kit_available": profile.edge_kit_available,
        "robot_tier_access": profile.robot_tier_access,
        "ros2_level": profile.ros2_level,
        "gazebo_level": profile.gazebo_level,
        "unity_level": profile.unity_level,
        "isaac_level": profile.isaac_level,
        "vla_level": profile.vla_level,
        "preferred_language": user.preferred_language if user else 'en',
        "is_personalized": profile.is_personalized,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }

    return PreferenceResponse.model_validate(response_data)


@router.put(
    "/preferences",
    response_model=PreferenceResponse,
    summary="Update user preferences",
    description="Update personalization preferences for the authenticated user"
)
async def update_user_preferences(
    preferences: PreferenceInput,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update personalization preferences for authenticated user.

    Args:
        preferences: Updated preference data
        user_id: Authenticated user ID (from JWT)
        db: Database session

    Returns:
        Updated preferences

    Raises:
        404: User has no preferences to update
        422: Invalid enum values
    """
    from src.models.user import User

    try:
        profile = await update_preferences(
            db,
            user_id=user_id,
            preferences=preferences.model_dump(exclude_unset=True),
            change_source="profile_page"
        )

        # Get user's preferred_language from users table
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        # Build response with preferred_language from user
        response_data = {
            "id": profile.id,
            "user_id": profile.user_id,
            "workstation_type": profile.workstation_type,
            "edge_kit_available": profile.edge_kit_available,
            "robot_tier_access": profile.robot_tier_access,
            "ros2_level": profile.ros2_level,
            "gazebo_level": profile.gazebo_level,
            "unity_level": profile.unity_level,
            "isaac_level": profile.isaac_level,
            "vla_level": profile.vla_level,
            "preferred_language": user.preferred_language if user else 'en',
            "is_personalized": profile.is_personalized,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }

        return PreferenceResponse.model_validate(response_data)

    except ValueError as e:
        if "has no preferences" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )


@router.delete(
    "/preferences",
    summary="Clear all preferences",
    description="Clear all personalization preferences for the authenticated user"
)
async def clear_user_preferences(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all personalization preferences for authenticated user.
    Sets all preference fields to None and is_personalized to False.

    Args:
        user_id: Authenticated user ID (from JWT)
        db: Database session

    Returns:
        Success message

    Raises:
        404: User has no preferences to clear
    """
    try:
        await clear_preferences(db, user_id=user_id, change_source="profile_page")
        return {"message": "Preferences cleared successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


class PreferenceHistoryResponse(BaseModel):
    """Response schema for preference history"""
    id: UUID
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    change_source: str
    changed_at: datetime

    class Config:
        from_attributes = True


@router.get(
    "/preferences/history",
    response_model=List[PreferenceHistoryResponse],
    summary="Get preference change history",
    description="Retrieve history of all preference changes for the authenticated user"
)
async def get_user_preference_history(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """
    Get preference change history for authenticated user.

    Args:
        user_id: Authenticated user ID (from JWT)
        db: Database session
        limit: Maximum number of history entries to return (default: 50)

    Returns:
        List of preference history entries, ordered by changed_at DESC
    """
    history = await get_preference_history(db, user_id=user_id, limit=limit)
    return [PreferenceHistoryResponse.model_validate(h) for h in history]
