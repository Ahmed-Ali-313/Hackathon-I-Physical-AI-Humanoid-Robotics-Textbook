import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_column():
    database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    
    conn = await asyncpg.connect(database_url)
    
    try:
        print("1. Dropping old constraint...")
        await conn.execute("ALTER TABLE personalization_profiles DROP CONSTRAINT IF EXISTS valid_edge_kit")
        print("✅ Constraint dropped")
        
        print("\n2. Changing column type to VARCHAR(50)...")
        await conn.execute("ALTER TABLE personalization_profiles ALTER COLUMN edge_kit_available TYPE VARCHAR(50) USING edge_kit_available::text")
        print("✅ Column type changed")
        
        print("\n3. Adding new constraint...")
        await conn.execute("""
            ALTER TABLE personalization_profiles
            ADD CONSTRAINT valid_edge_kit 
            CHECK (edge_kit_available IS NULL OR edge_kit_available IN ('none', 'jetson_nano', 'jetson_orin', 'raspberry_pi', 'other'))
        """)
        print("✅ Constraint added")
        
        print("\n4. Verifying change...")
        result = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'personalization_profiles'
            AND column_name = 'edge_kit_available'
        """)
        
        for row in result:
            print(f"  Column: {row['column_name']}")
            print(f"  Type: {row['data_type']}")
            print(f"  Max Length: {row['character_maximum_length']}")
        
        print("\n✅✅✅ MIGRATION SUCCESSFUL! ✅✅✅")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(fix_column())
