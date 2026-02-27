#!/usr/bin/env python3
"""
Backend startup test script.
Tests database connection, auth endpoints, and chat functionality.
"""

import asyncio
import sys
from sqlalchemy import text
from src.database import engine, AsyncSessionLocal
from src.services.auth_service import hash_password, verify_password
from src.config import settings

async def test_database_connection():
    """Test database connection."""
    print("\n1. Testing database connection...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("   ✅ Database connection successful")
                return True
            else:
                print("   ❌ Database connection failed: unexpected result")
                return False
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

async def test_auth_service():
    """Test authentication service."""
    print("\n2. Testing authentication service...")
    try:
        # Test password hashing
        test_password = "test123"
        hashed = hash_password(test_password)
        print(f"   ✅ Password hashing works (hash length: {len(hashed)})")

        # Test password verification
        if verify_password(test_password, hashed):
            print("   ✅ Password verification works")
        else:
            print("   ❌ Password verification failed")
            return False

        # Test wrong password
        if not verify_password("wrong", hashed):
            print("   ✅ Wrong password correctly rejected")
        else:
            print("   ❌ Wrong password incorrectly accepted")
            return False

        return True
    except Exception as e:
        print(f"   ❌ Auth service test failed: {e}")
        return False

async def test_configuration():
    """Test configuration."""
    print("\n3. Testing configuration...")
    try:
        print(f"   Database URL: {settings.database_url[:30]}...")
        print(f"   OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Not set'}")
        print(f"   Qdrant URL: {'✅ Set' if settings.qdrant_url else '❌ Not set'}")
        print(f"   JWT Secret: {'✅ Set' if settings.jwt_secret_key else '❌ Not set'}")
        print(f"   Environment: {settings.environment}")

        if not settings.openai_api_key:
            print("   ❌ OpenAI API key not configured")
            return False

        print("   ✅ Configuration looks good")
        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

async def test_tables_exist():
    """Test if required tables exist."""
    print("\n4. Testing database tables...")
    try:
        async with AsyncSessionLocal() as session:
            # Check if users table exists
            result = await session.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            ))
            users_exists = result.scalar()

            # Check if conversations table exists
            result = await session.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conversations')"
            ))
            conversations_exists = result.scalar()

            # Check if chat_messages table exists
            result = await session.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'chat_messages')"
            ))
            messages_exists = result.scalar()

            print(f"   Users table: {'✅ Exists' if users_exists else '❌ Missing'}")
            print(f"   Conversations table: {'✅ Exists' if conversations_exists else '❌ Missing'}")
            print(f"   Chat messages table: {'✅ Exists' if messages_exists else '❌ Missing'}")

            if users_exists and conversations_exists and messages_exists:
                print("   ✅ All required tables exist")
                return True
            else:
                print("   ❌ Some tables are missing")
                return False
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("Backend Startup Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_configuration())
    results.append(await test_database_connection())
    results.append(await test_tables_exist())
    results.append(await test_auth_service())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed! Backend is ready to start.")
        print("\nTo start the backend, run:")
        print("  cd backend")
        print("  ./venv/bin/python -m uvicorn src.main:app --reload --port 8001")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
