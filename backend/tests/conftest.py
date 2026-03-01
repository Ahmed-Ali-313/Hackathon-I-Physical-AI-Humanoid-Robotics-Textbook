"""
Pytest fixtures for backend tests

Provides:
- Database session fixtures
- Test user fixtures
- Authentication fixtures
- Test client fixtures
"""

import pytest
import pytest_asyncio
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

# Set test environment variables BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRATION_MINUTES"] = "30"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from src.database import Base
from src.main import app
from src.models.user import User
from src.models.personalization_profile import PersonalizationProfile
from src.models.translated_chapter import TranslatedChapter
from src.middleware.auth import create_access_token


# Test database URL (use in-memory async SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """Create test database engine for each test"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for each test"""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create FastAPI test client with overridden database dependency"""
    from src.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="testuser@example.com",
        password_hash="hashed_password_123"
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_with_profile(db_session: AsyncSession, test_user: User) -> User:
    """Create a test user with personalization profile"""
    profile = PersonalizationProfile(
        user_id=test_user.id,
        workstation_type="high_end_desktop",
        edge_kit_available="jetson_orin",
        ros2_level="intermediate",
        gazebo_level="beginner",
        is_personalized=True
    )
    db_session.add(profile)
    await db_session.flush()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authentication headers for test user"""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_with_profile(test_user_with_profile: User) -> dict:
    """Generate authentication headers for test user with profile"""
    token = create_access_token(str(test_user_with_profile.id))
    return {"Authorization": f"Bearer {token}"}
