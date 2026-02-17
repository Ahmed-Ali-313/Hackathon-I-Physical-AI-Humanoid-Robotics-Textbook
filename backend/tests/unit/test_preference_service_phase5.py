"""
Additional unit tests for preference_service - Phase 5

Tests:
- update_preferences() with audit logging
- Cache invalidation on update
- Preference history creation
"""

import pytest
from src.services.preference_service import update_preferences, _preference_cache


class TestPreferenceServicePhase5:
    """Test suite for Phase 5 preference service features"""

    @pytest.mark.asyncio
    async def test_update_preferences_creates_audit_log(self, db_session, test_user_with_profile):
        """Test that updating preferences creates audit log entries"""
        from src.models.preference_history import PreferenceHistory
        from sqlalchemy import select

        # Update preferences
        updated_prefs = {
            "ros2_level": "advanced",
            "gazebo_level": "intermediate"
        }
        await update_preferences(db_session, test_user_with_profile.id, updated_prefs)

        # Check audit log
        result = await db_session.execute(
            select(PreferenceHistory).where(
                PreferenceHistory.user_id == test_user_with_profile.id
            )
        )
        history_entries = result.scalars().all()

        assert len(history_entries) == 2
        field_names = [h.field_name for h in history_entries]
        assert "ros2_level" in field_names
        assert "gazebo_level" in field_names

    @pytest.mark.asyncio
    async def test_update_preferences_invalidates_cache(self, db_session, test_user_with_profile):
        """Test that updating preferences invalidates cache"""
        from src.services.preference_service import get_preferences

        # Get preferences (should cache)
        profile1 = await get_preferences(db_session, test_user_with_profile.id)
        assert profile1.ros2_level == "intermediate"

        # Update preferences
        await update_preferences(
            db_session,
            test_user_with_profile.id,
            {"ros2_level": "advanced"}
        )

        # Get preferences again (should fetch fresh from DB, not cache)
        profile2 = await get_preferences(db_session, test_user_with_profile.id)
        assert profile2.ros2_level == "advanced"

    @pytest.mark.asyncio
    async def test_update_preferences_tracks_old_values(self, db_session, test_user_with_profile):
        """Test that audit log correctly tracks old and new values"""
        from src.models.preference_history import PreferenceHistory
        from src.models.personalization_profile import PersonalizationProfile
        from sqlalchemy import select

        # Get original value using async query
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()
        original_value = profile.ros2_level

        # Update to "advanced"
        await update_preferences(
            db_session,
            test_user_with_profile.id,
            {"ros2_level": "advanced"}
        )

        # Check audit log has correct old/new values
        result = await db_session.execute(
            select(PreferenceHistory).where(
                PreferenceHistory.user_id == test_user_with_profile.id,
                PreferenceHistory.field_name == "ros2_level"
            )
        )
        history = result.scalar_one()

        assert history.old_value == original_value
        assert history.new_value == "advanced"

    @pytest.mark.asyncio
    async def test_update_preferences_only_logs_changed_fields(self, db_session, test_user_with_profile):
        """Test that only changed fields are logged"""
        from src.models.preference_history import PreferenceHistory
        from src.models.personalization_profile import PersonalizationProfile
        from sqlalchemy import select

        # Get current value using async query
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()
        current_value = profile.ros2_level

        # Update with same value (no change)
        await update_preferences(
            db_session,
            test_user_with_profile.id,
            {"ros2_level": current_value}  # Same value
        )

        # Check no audit log created for unchanged field
        result = await db_session.execute(
            select(PreferenceHistory).where(
                PreferenceHistory.user_id == test_user_with_profile.id
            )
        )
        history_entries = result.scalars().all()

        assert len(history_entries) == 0

    @pytest.mark.asyncio
    async def test_cache_invalidation_removes_entry(self, db_session, test_user_with_profile):
        """Test that cache invalidation actually removes cache entry"""
        from src.services.preference_service import get_preferences

        # Cache the preferences
        await get_preferences(db_session, test_user_with_profile.id)
        cache_key = f"user:{test_user_with_profile.id}"
        assert _preference_cache.get(cache_key) is not None

        # Update preferences (should invalidate cache)
        await update_preferences(
            db_session,
            test_user_with_profile.id,
            {"ros2_level": "advanced"}
        )

        # Cache should be invalidated
        assert _preference_cache.get(cache_key) is None
