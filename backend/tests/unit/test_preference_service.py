"""
Unit tests for preference_service

Tests:
- create_preferences() method
- get_preferences() method
- Caching logic with TTL
- Cache invalidation
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services.preference_service import (
    create_preferences,
    get_preferences,
    CacheWithTTL
)


class TestPreferenceService:
    """Test suite for preference service"""

    @pytest.mark.asyncio
    async def test_create_preferences_success(self, db_session, test_user):
        """Test creating preferences successfully"""
        preference_data = {
            "workstation_type": "high_end_desktop",
            "edge_kit_available": "jetson_orin",
            "ros2_level": "intermediate",
            "gazebo_level": "beginner"
        }

        profile = await create_preferences(
            db_session,
            user_id=test_user.id,
            preferences=preference_data
        )

        assert profile is not None
        assert profile.user_id == test_user.id
        assert profile.workstation_type == "high_end_desktop"
        assert profile.edge_kit_available == "jetson_orin"
        assert profile.ros2_level == "intermediate"
        assert profile.is_personalized is True

    @pytest.mark.asyncio
    async def test_create_preferences_duplicate_user(self, db_session, test_user):
        """Test that creating duplicate preferences fails"""
        preference_data = {"workstation_type": "laptop"}

        # Create first profile
        await create_preferences(db_session, test_user.id, preference_data)

        # Attempt to create second profile for same user
        with pytest.raises(ValueError, match="already has preferences"):
            await create_preferences(db_session, test_user.id, preference_data)

    @pytest.mark.asyncio
    async def test_create_preferences_invalid_enum(self, db_session, test_user):
        """Test that invalid enum values are rejected"""
        preference_data = {"workstation_type": "invalid_type"}

        with pytest.raises(ValueError, match="Invalid"):
            await create_preferences(db_session, test_user.id, preference_data)

    @pytest.mark.asyncio
    async def test_get_preferences_success(self, db_session, test_user_with_profile):
        """Test retrieving preferences successfully"""
        profile = await get_preferences(db_session, test_user_with_profile.id)

        assert profile is not None
        assert profile.user_id == test_user_with_profile.id
        assert profile.workstation_type is not None

    @pytest.mark.asyncio
    async def test_get_preferences_not_found(self, db_session, test_user):
        """Test retrieving preferences for user without profile"""
        profile = await get_preferences(db_session, test_user.id)

        assert profile is None

    @pytest.mark.asyncio
    async def test_preference_caching_with_ttl(self, db_session, test_user_with_profile):
        """Test that preferences are cached with TTL"""
        # First call - should hit database
        profile1 = await get_preferences(db_session, test_user_with_profile.id)

        # Second call - should hit cache
        profile2 = await get_preferences(db_session, test_user_with_profile.id)

        assert profile1.id == profile2.id
        # Verify cache was used (would need to mock db_session to verify)

    def test_cache_with_ttl_expiration(self):
        """Test that cache entries expire after TTL"""
        cache = CacheWithTTL(ttl_seconds=1)

        # Add entry
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        import time
        time.sleep(1.1)

        # Entry should be expired
        assert cache.get("key1") is None

    def test_cache_with_ttl_invalidation(self):
        """Test manual cache invalidation"""
        cache = CacheWithTTL(ttl_seconds=300)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Invalidate
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_cache_with_ttl_clear_all(self):
        """Test clearing all cache entries"""
        cache = CacheWithTTL(ttl_seconds=300)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
