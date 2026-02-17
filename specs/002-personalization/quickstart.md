# Quickstart Guide: User Personalization System

**Feature**: 002-personalization
**Date**: 2026-02-17
**Audience**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions for setting up the development environment, installing dependencies, and running the personalization system locally.

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: 20.x LTS or higher
- **Python**: 3.11 or higher
- **PostgreSQL**: 14+ (or Neon Postgres account)
- **Git**: Latest version
- **Code Editor**: VS Code recommended

---

## Part 1: Environment Setup

### 1.1 Clone Repository

```bash
cd /path/to/project
git checkout 002-personalization
```

### 1.2 Install Frontend Dependencies

```bash
cd textbook
npm install
```

**Key Dependencies Installed**:
- Docusaurus 3.x
- React 18+
- TypeScript 5.x

### 1.3 Install Backend Dependencies

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Key Dependencies** (requirements.txt):
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

### 1.4 Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/personalization_db
# For Neon Postgres:
# DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/personalization_db

# Authentication (Better-Auth)
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Cache Configuration
PREFERENCE_CACHE_TTL_SECONDS=300
PREFERENCE_CACHE_MAX_SIZE=1000

# Environment
ENVIRONMENT=development
```

Create `.env` file in `textbook/` directory:

```bash
# API Endpoint
REACT_APP_API_URL=http://localhost:8000/api/v1

# Feature Flags
REACT_APP_ENABLE_PERSONALIZATION=true
```

---

## Part 2: Database Setup

### 2.1 Create Database (Local PostgreSQL)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE personalization_db;

# Create user (if needed)
CREATE USER personalization_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE personalization_db TO personalization_user;

# Exit psql
\q
```

### 2.2 Run Migrations

```bash
cd backend
source venv/bin/activate

# Run database migrations
alembic upgrade head
```

**Migration Files** (in `backend/database/migrations/`):
- `001_create_users.sql` - Users table (Better-Auth)
- `002_create_personalization_profiles.sql` - Preference storage
- `003_create_content_metadata.sql` - Content tags
- `004_create_preference_history.sql` - Audit log

### 2.3 Verify Database Schema

```bash
psql -U personalization_user -d personalization_db

# List tables
\dt

# Expected output:
# users
# personalization_profiles
# content_metadata
# preference_history

# Exit
\q
```

---

## Part 3: Running the Application

### 3.1 Start Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**API Documentation**: http://localhost:8000/docs (Swagger UI)

### 3.2 Start Frontend Development Server

```bash
cd textbook
npm start
```

**Expected Output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### 3.3 Verify Integration

1. Open browser: http://localhost:3000
2. Navigate to signup page
3. Fill in personalization preferences
4. Check browser DevTools Network tab for API calls to http://localhost:8000

---

## Part 4: Development Workflow

### 4.1 Frontend Development

**File Structure**:
```
textbook/src/
├── components/
│   ├── PersonalizationForm/
│   │   ├── index.tsx
│   │   ├── styles.module.css
│   │   └── __tests__/
│   ├── ContentHighlight/
│   ├── ViewToggle/
│   └── PreferenceBanner/
├── hooks/
│   ├── usePersonalization.ts
│   └── useContentMetadata.ts
├── contexts/
│   └── PersonalizationContext.tsx
└── services/
    └── personalizationApi.ts
```

**Run Frontend Tests**:
```bash
cd textbook
npm test
```

**Build for Production**:
```bash
npm run build
```

### 4.2 Backend Development

**File Structure**:
```
backend/src/
├── models/
│   ├── user.py
│   ├── personalization_profile.py
│   ├── content_metadata.py
│   └── preference_history.py
├── services/
│   ├── preference_service.py
│   └── matching_service.py
├── api/
│   ├── preferences.py
│   └── content.py
└── middleware/
    └── auth.py
```

**Run Backend Tests**:
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Run Specific Test File**:
```bash
pytest tests/unit/test_preference_service.py -v
```

**Check Code Coverage**:
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### 4.3 Database Migrations

**Create New Migration**:
```bash
cd backend
alembic revision -m "Add new field to personalization_profiles"
```

**Apply Migration**:
```bash
alembic upgrade head
```

**Rollback Migration**:
```bash
alembic downgrade -1
```

---

## Part 5: Content Metadata Tagging

### 5.1 Add Metadata to Content Files

Edit Markdown files in `textbook/docs/`:

```markdown
---
id: nvidia-isaac-sim-intro
title: Introduction to NVIDIA Isaac Sim
personalization:
  hardware:
    - rtx_12gb
    - rtx_24gb
  software:
    ros2_level: intermediate
    isaac_level: beginner
---

# Introduction to NVIDIA Isaac Sim

Your content here...
```

### 5.2 Sync Metadata to Database

```bash
cd backend
source venv/bin/activate
python scripts/sync_content_metadata.py
```

**Expected Output**:
```
[INFO] Scanning docs directory...
[INFO] Found 47 markdown files
[INFO] Processing nvidia-isaac-sim-intro.md...
[INFO] Synced metadata for content_id: nvidia-isaac-sim-intro
[INFO] Processing ros2-topics-services.md...
[INFO] Synced metadata for content_id: ros2-topics-services
...
[SUCCESS] Synced 47 content metadata entries
```

### 5.3 Verify Metadata in Database

```bash
psql -U personalization_user -d personalization_db

SELECT content_id, title, hardware_tags, software_requirements
FROM content_metadata
LIMIT 5;
```

---

## Part 6: Testing Scenarios

### 6.1 Test Signup with Personalization

1. Navigate to http://localhost:3000/signup
2. Fill in email and password
3. Select preferences:
   - Workstation: "Workstation with RTX GPU (12GB+ VRAM)"
   - ROS 2 Level: "Intermediate"
   - Isaac Level: "Beginner"
4. Submit form
5. Verify API call in DevTools: `POST /api/v1/preferences`
6. Check database:
   ```sql
   SELECT * FROM personalization_profiles WHERE user_id = 'your-user-id';
   ```

### 6.2 Test Personalized Content View

1. Log in with personalized account
2. Navigate to a chapter (e.g., NVIDIA Isaac Sim intro)
3. Verify "Recommended for your setup" badge appears
4. Click toggle button to switch to "Full Content View"
5. Verify highlighting is removed

### 6.3 Test Preference Updates

1. Navigate to http://localhost:3000/profile
2. Update ROS 2 level from "Intermediate" to "Advanced"
3. Save changes
4. Verify API call: `PUT /api/v1/preferences`
5. Navigate back to a chapter
6. Verify recommendations updated immediately (no logout required)

### 6.4 Test Preference History

1. Make several preference updates
2. Call API: `GET /api/v1/preferences/history`
3. Verify audit log shows all changes with timestamps

---

## Part 7: Troubleshooting

### Issue: Database Connection Failed

**Symptom**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in `.env` file
3. Verify database exists: `psql -l | grep personalization_db`
4. Check firewall/network settings

### Issue: JWT Token Invalid

**Symptom**: `401 Unauthorized` on API calls

**Solution**:
1. Verify JWT_SECRET_KEY matches between Better-Auth and backend
2. Check token expiration (JWT_EXPIRATION_MINUTES)
3. Clear browser localStorage and re-login
4. Verify Authorization header format: `Bearer <token>`

### Issue: Content Metadata Not Loading

**Symptom**: No personalized recommendations appear

**Solution**:
1. Run metadata sync script: `python scripts/sync_content_metadata.py`
2. Verify frontmatter format in .md files
3. Check database: `SELECT COUNT(*) FROM content_metadata;`
4. Clear preference cache and reload page

### Issue: Frontend Build Fails

**Symptom**: `npm run build` errors

**Solution**:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version: `node --version` (should be 20.x)
4. Clear npm cache: `npm cache clean --force`

---

## Part 8: Performance Optimization

### 8.1 Enable Query Logging (Development Only)

In `backend/src/database.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL query logging
    pool_size=5,
    max_overflow=15
)
```

### 8.2 Monitor Cache Hit Rate

Add logging to preference cache:
```python
import logging

logger = logging.getLogger(__name__)

def get_preferences(user_id: str):
    cached = preference_cache.get(user_id)
    if cached:
        logger.info(f"Cache HIT for user {user_id}")
        return cached
    logger.info(f"Cache MISS for user {user_id}")
    # ... fetch from database
```

### 8.3 Database Connection Pool Tuning

Adjust pool size based on load testing:
```python
# For higher concurrency (1000+ users)
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=30,
    pool_pre_ping=True
)
```

---

## Part 9: Deployment Checklist

Before deploying to production:

- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Set ENVIRONMENT=production in .env
- [ ] Update CORS_ORIGINS to production domain
- [ ] Run all tests: `npm test && pytest tests/`
- [ ] Build frontend: `npm run build`
- [ ] Run database migrations on production DB
- [ ] Sync content metadata to production DB
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Test signup flow end-to-end
- [ ] Test preference updates end-to-end
- [ ] Verify API rate limiting (if applicable)
- [ ] Load test with expected user count

---

## Part 10: Useful Commands Reference

### Frontend
```bash
npm start              # Start dev server
npm test               # Run tests
npm run build          # Build for production
npm run serve          # Serve production build locally
```

### Backend
```bash
uvicorn src.main:app --reload           # Start dev server
pytest tests/ -v                        # Run tests with verbose output
pytest tests/ --cov=src                 # Run tests with coverage
alembic upgrade head                    # Apply migrations
alembic downgrade -1                    # Rollback one migration
python scripts/sync_content_metadata.py # Sync content metadata
```

### Database
```bash
psql -U personalization_user -d personalization_db  # Connect to DB
\dt                                                  # List tables
\d personalization_profiles                          # Describe table
SELECT COUNT(*) FROM personalization_profiles;       # Count records
```

---

## Support

For issues or questions:
- Check [spec.md](./spec.md) for requirements
- Check [research.md](./research.md) for technical decisions
- Check [data-model.md](./data-model.md) for database schema
- Check [contracts/preferences.yaml](./contracts/preferences.yaml) for API documentation

---

**Last Updated**: 2026-02-17
**Feature Branch**: 002-personalization
