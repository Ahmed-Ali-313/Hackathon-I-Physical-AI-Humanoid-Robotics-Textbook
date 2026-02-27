import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_schema():
    database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    
    conn = await asyncpg.connect(database_url)
    
    # Check column type
    result = await conn.fetch("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'personalization_profiles'
        AND column_name = 'edge_kit_available'
    """)
    
    print("Current schema for edge_kit_available:")
    for row in result:
        print(f"  Column: {row['column_name']}")
        print(f"  Type: {row['data_type']}")
        print(f"  Max Length: {row['character_maximum_length']}")
    
    await conn.close()

asyncio.run(check_schema())
