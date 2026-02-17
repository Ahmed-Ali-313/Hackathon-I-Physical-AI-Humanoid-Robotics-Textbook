"""
Unit tests for User model

Tests:
- User model creation and validation
- Email uniqueness constraint
- Timestamp auto-population
- Relationship with PersonalizationProfile
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.models.user import User


class TestUserModel:
    """Test suite for User model"""

    @pytest.mark.asyncio
    async def test_user_creation(self, db_session):
        """Test creating a valid user"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password_123"
        )
        db_session.add(user)
        await db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_user_email_uniqueness(self, db_session):
        """Test that duplicate emails are rejected"""
        user1 = User(email="duplicate@example.com", password_hash="hash1")
        db_session.add(user1)
        await db_session.commit()

        user2 = User(email="duplicate@example.com", password_hash="hash2")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_timestamps_auto_populate(self, db_session):
        """Test that timestamps are automatically set"""
        user = User(email="timestamp@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= user.updated_at

    @pytest.mark.asyncio
    async def test_user_profile_relationship(self, db_session):
        """Test relationship between User and PersonalizationProfile"""
        from src.models.personalization_profile import PersonalizationProfile

        user = User(email="profile@example.com", password_hash="hash")
        db_session.add(user)
        await db_session.commit()

        profile = PersonalizationProfile(
            user_id=user.id,
            workstation_type="high_end_desktop",
            is_personalized=True
        )
        db_session.add(profile)
        await db_session.commit()

        # Refresh to load relationship
        await db_session.refresh(user)

        # Test relationship access
        assert user.personalization_profile is not None
        assert user.personalization_profile.user_id == user.id

    @pytest.mark.asyncio
    async def test_user_required_fields(self, db_session):
        """Test that required fields cannot be null"""
        user = User(password_hash="hash")  # Missing email
        db_session.add(user)

        with pytest.raises(IntegrityError):
            await db_session.commit()
