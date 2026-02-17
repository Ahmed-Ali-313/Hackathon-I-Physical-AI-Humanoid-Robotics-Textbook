"""
Unit tests for PersonalizationProfile model

Tests:
- Profile creation with valid enum values
- Enum validation (reject invalid values)
- State transitions (is_personalized flag)
- Default values
- Relationship with User
"""

import pytest
from sqlalchemy.exc import IntegrityError
from src.models.personalization_profile import PersonalizationProfile


class TestPersonalizationProfileModel:
    """Test suite for PersonalizationProfile model"""

    @pytest.mark.asyncio
    async def test_profile_creation_with_valid_enums(self, db_session, test_user):
        """Test creating profile with valid enum values"""
        profile = PersonalizationProfile(
            user_id=test_user.id,
            workstation_type="high_end_desktop",
            edge_kit_available="jetson_orin",
            robot_tier_access="tier_2",
            ros2_level="intermediate",
            gazebo_level="beginner",
            unity_level="advanced",
            isaac_level="intermediate",
            vla_level="none",
            is_personalized=True
        )
        db_session.add(profile)
        await db_session.commit()

        assert profile.id is not None
        assert profile.workstation_type == "high_end_desktop"
        assert profile.edge_kit_available == "jetson_orin"
        assert profile.robot_tier_access == "tier_2"
        assert profile.ros2_level == "intermediate"
        assert profile.is_personalized is True

    @pytest.mark.asyncio
    async def test_profile_invalid_workstation_type(self, db_session, test_user):
        """Test that invalid workstation_type is rejected"""
        profile = PersonalizationProfile(
            user_id=test_user.id,
            workstation_type="invalid_type",
            is_personalized=True
        )
        db_session.add(profile)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_profile_invalid_experience_level(self, db_session, test_user):
        """Test that invalid experience level is rejected"""
        profile = PersonalizationProfile(
            user_id=test_user.id,
            ros2_level="expert_plus",  # Invalid level
            is_personalized=True
        )
        db_session.add(profile)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_profile_default_is_personalized(self, db_session, test_user):
        """Test that is_personalized defaults to False"""
        profile = PersonalizationProfile(user_id=test_user.id)
        db_session.add(profile)
        await db_session.commit()

        assert profile.is_personalized is False

    @pytest.mark.asyncio
    async def test_profile_user_relationship(self, db_session, test_user):
        """Test relationship between Profile and User"""
        profile = PersonalizationProfile(
            user_id=test_user.id,
            workstation_type="laptop",
            is_personalized=True
        )
        db_session.add(profile)
        await db_session.commit()

        # Refresh to load relationship
        await db_session.refresh(profile)

        # Test relationship access
        assert profile.user is not None
        assert profile.user.id == test_user.id
        assert profile.user.email == test_user.email

    @pytest.mark.asyncio
    async def test_profile_one_per_user(self, db_session, test_user):
        """Test that each user can have only one profile"""
        profile1 = PersonalizationProfile(user_id=test_user.id, is_personalized=True)
        db_session.add(profile1)
        await db_session.commit()

        profile2 = PersonalizationProfile(user_id=test_user.id, is_personalized=True)
        db_session.add(profile2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_profile_nullable_fields(self, db_session, test_user):
        """Test that preference fields can be null"""
        profile = PersonalizationProfile(
            user_id=test_user.id,
            is_personalized=False
        )
        db_session.add(profile)
        await db_session.commit()

        assert profile.workstation_type is None
        assert profile.edge_kit_available is None
        assert profile.robot_tier_access is None
        assert profile.ros2_level is None
