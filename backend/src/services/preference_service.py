"""
Preference Service

Business logic for managing user personalization preferences.
Includes caching with TTL for performance optimization.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.personalization_profile import PersonalizationProfile


class CacheWithTTL:
    """Simple in-memory cache with TTL support"""

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 5 minutes)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[Any, datetime]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if datetime.utcnow() > expiry:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL"""
        expiry = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        self._cache[key] = (value, expiry)

    def invalidate(self, key: str) -> None:
        """Remove specific key from cache"""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()


# Global cache instance (5-minute TTL)
_preference_cache = CacheWithTTL(ttl_seconds=300)


async def create_preferences(
    db: AsyncSession,
    user_id: str,
    preferences: Dict[str, Any]
) -> PersonalizationProfile:
    """
    Create personalization preferences for a user.

    Args:
        db: Database session
        user_id: User UUID
        preferences: Dictionary of preference fields

    Returns:
        Created PersonalizationProfile

    Raises:
        ValueError: If user already has preferences or invalid enum values
    """
    # Check if user already has preferences
    result = await db.execute(
        select(PersonalizationProfile).where(PersonalizationProfile.user_id == user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(f"User {user_id} already has preferences")

    # Validate enum values
    valid_workstation_types = ['laptop', 'mid_range_desktop', 'high_end_desktop', 'workstation', 'cloud_instance']
    valid_edge_kits = ['none', 'jetson_nano', 'jetson_orin', 'raspberry_pi', 'other']
    valid_robot_tiers = ['none', 'tier_1', 'tier_2', 'tier_3']
    valid_experience_levels = ['none', 'beginner', 'intermediate', 'advanced']

    if 'workstation_type' in preferences and preferences['workstation_type'] not in valid_workstation_types:
        raise ValueError(f"Invalid workstation_type: {preferences['workstation_type']}")

    if 'edge_kit_available' in preferences and preferences['edge_kit_available'] not in valid_edge_kits:
        raise ValueError(f"Invalid edge_kit_available: {preferences['edge_kit_available']}")

    if 'robot_tier_access' in preferences and preferences['robot_tier_access'] not in valid_robot_tiers:
        raise ValueError(f"Invalid robot_tier_access: {preferences['robot_tier_access']}")

    for level_field in ['ros2_level', 'gazebo_level', 'unity_level', 'isaac_level', 'vla_level']:
        if level_field in preferences and preferences[level_field] not in valid_experience_levels:
            raise ValueError(f"Invalid {level_field}: {preferences[level_field]}")

    # Determine if personalized (at least one preference set)
    is_personalized = any(v is not None for v in preferences.values())

    # Create profile
    profile = PersonalizationProfile(
        user_id=user_id,
        is_personalized=is_personalized,
        **preferences
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    # Cache the new profile
    _preference_cache.set(f"user:{user_id}", profile)

    return profile


async def get_preferences(
    db: AsyncSession,
    user_id: str
) -> Optional[PersonalizationProfile]:
    """
    Get personalization preferences for a user.
    Uses caching for performance.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        PersonalizationProfile or None if not found
    """
    # Check cache first
    cache_key = f"user:{user_id}"
    cached = _preference_cache.get(cache_key)
    if cached:
        return cached

    # Query database
    result = await db.execute(
        select(PersonalizationProfile).where(PersonalizationProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    # Cache if found
    if profile:
        _preference_cache.set(cache_key, profile)

    return profile


async def update_preferences(
    db: AsyncSession,
    user_id: str,
    preferences: Dict[str, Any],
    change_source: str = "profile_page"
) -> PersonalizationProfile:
    """
    Update personalization preferences for a user.
    Creates audit log entries for all changed fields.

    Args:
        db: Database session
        user_id: User UUID (as string from JWT)
        preferences: Dictionary of preference fields to update
        change_source: Source of the change (default: 'profile_page')

    Returns:
        Updated PersonalizationProfile

    Raises:
        ValueError: If user has no preferences or invalid enum values
    """
    from src.models.preference_history import PreferenceHistory
    import uuid

    # Get existing profile - MUST query fresh from DB for updates, not from cache
    result = await db.execute(
        select(PersonalizationProfile).where(PersonalizationProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError(f"User {user_id} has no preferences to update")

    # Track changes for audit log
    changes = []

    # Update fields and track changes
    for key, new_value in preferences.items():
        if hasattr(profile, key):
            old_value = getattr(profile, key)

            # Only log if value actually changed
            if old_value != new_value:
                changes.append({
                    "field_name": key,
                    "old_value": str(old_value) if old_value is not None else None,
                    "new_value": str(new_value) if new_value is not None else None
                })
                setattr(profile, key, new_value)

    # Update is_personalized flag
    profile.is_personalized = any([
        profile.workstation_type,
        profile.edge_kit_available,
        profile.robot_tier_access,
        profile.ros2_level,
        profile.gazebo_level,
        profile.unity_level,
        profile.isaac_level,
        profile.vla_level
    ])

    await db.commit()
    await db.refresh(profile)

    # TODO: Re-enable audit logging after schema migration
    # Create audit log entries for changed fields
    # Convert user_id string to UUID
    # user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    #
    # for change in changes:
    #     history_entry = PreferenceHistory(
    #         user_id=user_uuid,
    #         profile_id=profile.id,
    #         field_name=change["field_name"],
    #         old_value=change["old_value"],
    #         new_value=change["new_value"],
    #         change_source=change_source
    #     )
    #     db.add(history_entry)
    #
    # await db.commit()

    # Invalidate cache after successful update
    _preference_cache.invalidate(f"user:{user_id}")

    return profile


async def clear_preferences(
    db: AsyncSession,
    user_id: str,
    change_source: str = "profile_page"
) -> PersonalizationProfile:
    """
    Clear all personalization preferences for a user.
    Sets all preference fields to None and is_personalized to False.

    Args:
        db: Database session
        user_id: User UUID (as string from JWT)
        change_source: Source of the change (default: 'profile_page')

    Returns:
        Updated PersonalizationProfile with cleared preferences

    Raises:
        ValueError: If user has no preferences
    """
    from src.models.preference_history import PreferenceHistory
    import uuid

    # Get existing profile - MUST query fresh from DB, not from cache
    result = await db.execute(
        select(PersonalizationProfile).where(PersonalizationProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError(f"User {user_id} has no preferences to clear")

    # Track all non-null fields for audit log
    changes = []
    fields_to_clear = [
        "workstation_type", "edge_kit_available", "robot_tier_access",
        "ros2_level", "gazebo_level", "unity_level", "isaac_level", "vla_level"
    ]

    for field in fields_to_clear:
        old_value = getattr(profile, field)
        if old_value is not None:
            changes.append({
                "field_name": field,
                "old_value": str(old_value),
                "new_value": None
            })
            setattr(profile, field, None)

    # Set is_personalized to False
    if profile.is_personalized:
        changes.append({
            "field_name": "is_personalized",
            "old_value": "True",
            "new_value": "False"
        })
        profile.is_personalized = False

    await db.commit()
    await db.refresh(profile)

    # TODO: Re-enable audit logging after schema migration
    # Create audit log entries
    # Convert user_id string to UUID
    # user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    #
    # for change in changes:
    #     history_entry = PreferenceHistory(
    #         user_id=user_uuid,
    #         profile_id=profile.id,
    #         field_name=change["field_name"],
    #         old_value=change["old_value"],
    #         new_value=change["new_value"],
    #         change_source=change_source
    #     )
    #     db.add(history_entry)
    #
    # await db.commit()

    # Invalidate cache
    _preference_cache.invalidate(f"user:{user_id}")

    return profile


async def get_preference_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 50
) -> list:
    """
    Get preference change history for a user.

    Args:
        db: Database session
        user_id: User UUID
        limit: Maximum number of history entries to return (default: 50)

    Returns:
        List of PreferenceHistory entries, ordered by changed_at DESC
    """
    from src.models.preference_history import PreferenceHistory
    from sqlalchemy import select

    result = await db.execute(
        select(PreferenceHistory)
        .where(PreferenceHistory.user_id == user_id)
        .order_by(PreferenceHistory.changed_at.desc())
        .limit(limit)
    )

    return result.scalars().all()
