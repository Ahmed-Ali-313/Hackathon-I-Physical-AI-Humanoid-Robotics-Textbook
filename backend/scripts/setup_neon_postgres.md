# Setup Neon Postgres for Production

## Current Credentials (from .env)
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_hBo1KXTMZp6j@ep-snowy-night-aiwqjasr-pooler.c-4.us-east-1.aws.neon.tech/neondb?ssl=require
```

## Steps to Switch from SQLite to Neon Postgres

### 1. Update .env
Uncomment the Neon Postgres DATABASE_URL and comment out SQLite:
```bash
# Database Configuration
# SQLite (for local testing)
# DATABASE_URL=sqlite+aiosqlite:///./app.db

# Neon Postgres (for production)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_hBo1KXTMZp6j@ep-snowy-night-aiwqjasr-pooler.c-4.us-east-1.aws.neon.tech/neondb?ssl=require
```

### 2. Create Tables in Neon Postgres

**Option A: Using Python Script**
```bash
cd backend
./venv/bin/python scripts/create_neon_tables.py
```

**Option B: Using Alembic Migrations** (if configured)
```bash
cd backend
./venv/bin/alembic upgrade head
```

**Option C: Manual SQL** (connect to Neon and run):
```sql
-- Run the SQL from backend/alembic/versions/*.py migration files
-- Or use the create_tables.sql script if available
```

### 3. Verify Tables Created
```bash
# Connect to Neon Postgres
psql "postgresql://neondb_owner:npg_hBo1KXTMZp6j@ep-snowy-night-aiwqjasr-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# List tables
\dt

# Should see:
# - users
# - personalization_profiles
# - content_metadata
# - preference_history
# - conversations
# - chat_messages
# - chat_sessions
```

### 4. Restart Backend
```bash
cd backend
./venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

## Notes
- SQLite is fine for testing but Neon Postgres is needed for production
- All chat data in SQLite will need to be migrated if you switch
- Neon Postgres supports concurrent connections better than SQLite
