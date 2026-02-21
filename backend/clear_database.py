#!/usr/bin/env python3
"""
Clear all user data from the database
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models.user import User
from src.models.personalization_profile import PersonalizationProfile
from src.models.preference_history import PreferenceHistory

# Database URL
DATABASE_URL = "sqlite:///./app.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_database():
    """Clear all user data from database"""
    db = SessionLocal()
    try:
        # Delete in order due to foreign key constraints
        deleted_history = db.query(PreferenceHistory).delete()
        deleted_profiles = db.query(PersonalizationProfile).delete()
        deleted_users = db.query(User).delete()

        db.commit()

        print(f"✅ Database cleared successfully!")
        print(f"   - Deleted {deleted_history} preference history records")
        print(f"   - Deleted {deleted_profiles} personalization profiles")
        print(f"   - Deleted {deleted_users} users")

        # Verify
        user_count = db.query(User).count()
        profile_count = db.query(PersonalizationProfile).count()
        history_count = db.query(PreferenceHistory).count()

        print(f"\n✅ Verification:")
        print(f"   - Users: {user_count}")
        print(f"   - Profiles: {profile_count}")
        print(f"   - History: {history_count}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Clearing database...")
    clear_database()
