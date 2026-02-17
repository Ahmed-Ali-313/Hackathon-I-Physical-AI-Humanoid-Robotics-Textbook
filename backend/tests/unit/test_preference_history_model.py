"""
Unit tests for PreferenceHistory model

Tests:
- PreferenceHistory creation with audit fields
- Relationship with User and PersonalizationProfile
- Change tracking (field_name, old_value, new_value)
- Change source validation
- Timestamp auto-population
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.models.preference_history import PreferenceHistory


class TestPreferenceHistoryModel:
    """Test suite for PreferenceHistory model"""

    @pytest.mark.asyncio
    async def test_preference_history_creation(self, db_session, test_user_with_profile):
        """Test creating preference history entry"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="ros2_level",
            old_value="beginner",
            new_value="intermediate",
            change_source="profile_page"
        )
        db_session.add(history)
        await db_session.commit()

        assert history.id is not None
        assert history.field_name == "ros2_level"
        assert history.old_value == "beginner"
        assert history.new_value == "intermediate"
        assert isinstance(history.changed_at, datetime)

    @pytest.mark.asyncio
    async def test_preference_history_user_relationship(self, db_session, test_user_with_profile):
        """Test relationship between PreferenceHistory and User"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="workstation_type",
            old_value="laptop",
            new_value="high_end_desktop",
            change_source="profile_page"
        )
        db_session.add(history)
        await db_session.commit()
        await db_session.refresh(history)

        assert history.user is not None
        assert history.user.id == test_user_with_profile.id

    @pytest.mark.asyncio
    async def test_preference_history_invalid_change_source(self, db_session, test_user_with_profile):
        """Test that invalid change_source is rejected"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="ros2_level",
            old_value="beginner",
            new_value="intermediate",
            change_source="invalid_source"
        )
        db_session.add(history)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_preference_history_null_values(self, db_session, test_user_with_profile):
        """Test that old_value and new_value can be null"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="edge_kit_available",
            old_value=None,
            new_value="jetson_orin",
            change_source="signup"
        )
        db_session.add(history)
        await db_session.commit()

        assert history.old_value is None
        assert history.new_value == "jetson_orin"

    @pytest.mark.asyncio
    async def test_preference_history_multiple_entries(self, db_session, test_user_with_profile):
        """Test creating multiple history entries for same user"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history1 = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="ros2_level",
            old_value="beginner",
            new_value="intermediate",
            change_source="profile_page"
        )
        history2 = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="gazebo_level",
            old_value="none",
            new_value="beginner",
            change_source="profile_page"
        )
        db_session.add_all([history1, history2])
        await db_session.commit()

        assert history1.id != history2.id
        assert history1.field_name != history2.field_name

    @pytest.mark.asyncio
    async def test_preference_history_timestamp_auto_populate(self, db_session, test_user_with_profile):
        """Test that changed_at timestamp is automatically set"""
        from sqlalchemy import select
        from src.models.personalization_profile import PersonalizationProfile

        # Get profile_id properly
        result = await db_session.execute(
            select(PersonalizationProfile).where(
                PersonalizationProfile.user_id == test_user_with_profile.id
            )
        )
        profile = result.scalar_one()

        history = PreferenceHistory(
            user_id=test_user_with_profile.id,
            profile_id=profile.id,
            field_name="unity_level",
            old_value="none",
            new_value="beginner",
            change_source="profile_page"
        )
        db_session.add(history)
        await db_session.commit()

        assert history.changed_at is not None
        assert isinstance(history.changed_at, datetime)
