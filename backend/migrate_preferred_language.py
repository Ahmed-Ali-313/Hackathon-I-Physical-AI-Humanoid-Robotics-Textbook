"""
Database Migration: Add preferred_language to personalization_profiles

Run this script to add the preferred_language column to the production database.
"""
import asyncio
import asyncpg
import os

async def run_migration():
    # Connect to Neon database
    DATABASE_URL = "postgresql://neondb_owner:npg_hBo1KXTMZp6j@ep-snowy-night-aiwqjasr-pooler.c-4.us-east-1.aws.neon.tech/neondb?ssl=require"

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("Adding preferred_language column...")
        await conn.execute("""
            ALTER TABLE personalization_profiles
            ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en'
        """)
        print("✅ Column added successfully")

        print("Adding check constraint...")
        await conn.execute("""
            ALTER TABLE personalization_profiles
            DROP CONSTRAINT IF EXISTS valid_preferred_language;

            ALTER TABLE personalization_profiles
            ADD CONSTRAINT valid_preferred_language
            CHECK (preferred_language IS NULL OR preferred_language IN ('en', 'ur'))
        """)
        print("✅ Constraint added successfully")

        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
