"""
Initialize Database Tables

Creates all tables defined in SQLAlchemy models.
"""
import asyncio
from src.database import init_db, engine
from src.models.user import User
from src.models.personalization_profile import PersonalizationProfile
from src.models.content_metadata import ContentMetadata
from src.models.preference_history import PreferenceHistory


async def main():
    print("Initializing database tables...")
    await init_db()
    print("✅ Database tables created successfully!")

    # Close engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
