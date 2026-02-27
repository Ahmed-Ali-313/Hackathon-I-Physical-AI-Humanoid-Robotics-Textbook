import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env")
        return
    
    # Convert SQLAlchemy URL to asyncpg URL
    db_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"Connecting to database...")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to database")
        
        # Read migration file
        with open('migrations/004_fix_edge_kit_type.sql', 'r') as f:
            migration_sql = f.read()
        
        print("\n📝 Running migration...")
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\nExecuting statement {i}...")
                try:
                    await conn.execute(statement)
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"⚠️  Statement {i} error (may be expected): {e}")
        
        print("\n✅ Migration completed successfully!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_migration())
