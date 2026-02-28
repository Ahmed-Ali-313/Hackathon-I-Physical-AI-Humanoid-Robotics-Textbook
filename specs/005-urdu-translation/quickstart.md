# Quickstart Guide: Urdu Translation

**Feature**: 005-urdu-translation
**Date**: 2026-02-28
**Purpose**: Setup instructions, development workflow, and testing procedures

## Overview

This guide provides step-by-step instructions for setting up the development environment, implementing the Urdu Translation feature, and running tests.

---

## Prerequisites

### Required Software

- **Python**: 3.12 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14 or higher (or Neon Serverless Postgres account)
- **Git**: Latest version

### Required Accounts

- **OpenAI API**: Valid API key with GPT-4o-mini access
- **Neon Postgres**: Database URL and credentials (production)
- **Google Fonts**: No account needed (CDN access)

### Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/textbook_dev
# Or for Neon Serverless Postgres:
# DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/textbook

# OpenAI API
OPENAI_API_KEY=sk-proj-xxx

# JWT Authentication
JWT_SECRET=your-secret-key-here
JWT_EXPIRY_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_TRANSLATION=10  # requests per minute
RATE_LIMIT_CACHE=100  # requests per minute
```

---

## Setup Instructions

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ai-native-book
git checkout 005-urdu-translation
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install new dependencies for translation
pip install openai hashlib  # hashlib is built-in, but listed for clarity

# Verify installation
python -c "import openai; print('OpenAI SDK installed')"
```

### Step 3: Database Setup

```bash
# Run migrations
python scripts/migrate.py 006_add_translation_tables.sql
python scripts/migrate.py 007_add_user_language_preference.sql

# Verify tables created
psql $DATABASE_URL -c "\d translated_chapters"
psql $DATABASE_URL -c "\d users"

# Expected output:
# translated_chapters table with columns: id, chapter_id, language_code, translated_content, original_hash, version, created_at, updated_at
# users table with new column: preferred_language
```

### Step 4: Frontend Setup

```bash
cd ../textbook

# Install dependencies
npm install

# Verify Docusaurus version
npm list @docusaurus/core
# Expected: @docusaurus/core@3.x.x
```

### Step 5: Font Setup

Add Google Fonts import to `textbook/src/theme/fonts.css`:

```css
/* Import Noto Nastaliq Urdu and Noto Sans Arabic */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&family=Noto+Sans+Arabic:wght@400;600&display=swap');
```

### Step 6: Verify Setup

```bash
# Backend health check
cd backend
python -m uvicorn src.main:app --reload --port 8001

# In another terminal, test health endpoint
curl http://localhost:8001/api/health
# Expected: {"status": "healthy"}

# Frontend dev server
cd textbook
npm start -- --port 3001

# Open browser: http://localhost:3001
```

---

## Development Workflow

### Phase 1: Backend Implementation (TDD)

#### 1.1 Translation Service (Unit Tests First)

```bash
cd backend

# Write tests first
touch tests/unit/test_translation_service.py

# Run tests (should fail - RED)
pytest tests/unit/test_translation_service.py -v

# Implement service
touch src/services/translation_service.py

# Run tests (should pass - GREEN)
pytest tests/unit/test_translation_service.py -v

# Refactor if needed
```

**Test Example** (`tests/unit/test_translation_service.py`):

```python
import pytest
from src.services.translation_service import TranslationService

@pytest.mark.asyncio
async def test_translate_preserves_technical_terms():
    """Test that technical terms remain in English."""
    service = TranslationService()
    content = "ROS 2 is a robotics middleware."

    translated = await service.translate(
        chapter_id="test-chapter",
        content=content,
        language_code="ur"
    )

    assert "ROS 2" in translated
    assert "robotics middleware" in translated
```

#### 1.2 Cache Service (Unit Tests First)

```bash
# Write tests
touch tests/unit/test_cache_service.py

# Run tests (RED)
pytest tests/unit/test_cache_service.py -v

# Implement service
touch src/services/cache_service.py

# Run tests (GREEN)
pytest tests/unit/test_cache_service.py -v
```

#### 1.3 Validation Service (Unit Tests First)

```bash
# Write tests
touch tests/unit/test_validation_service.py

# Run tests (RED)
pytest tests/unit/test_validation_service.py -v

# Implement service
touch src/services/validation_service.py

# Run tests (GREEN)
pytest tests/unit/test_validation_service.py -v
```

#### 1.4 API Endpoints (Integration Tests First)

```bash
# Write tests
touch tests/integration/test_translation_api.py

# Run tests (RED)
pytest tests/integration/test_translation_api.py -v

# Implement API
touch src/api/translation.py

# Run tests (GREEN)
pytest tests/integration/test_translation_api.py -v
```

### Phase 2: Frontend Implementation (TDD)

#### 2.1 Translation Component (Unit Tests First)

```bash
cd textbook

# Write tests
touch src/components/TranslationControl/TranslationControl.test.tsx

# Run tests (RED)
npm test -- TranslationControl.test.tsx

# Implement component
mkdir -p src/components/TranslationControl
touch src/components/TranslationControl/index.tsx
touch src/components/TranslationControl/styles.module.css

# Run tests (GREEN)
npm test -- TranslationControl.test.tsx
```

#### 2.2 Translation Hook (Unit Tests First)

```bash
# Write tests
touch src/hooks/useTranslation.test.ts

# Run tests (RED)
npm test -- useTranslation.test.ts

# Implement hook
touch src/hooks/useTranslation.ts

# Run tests (GREEN)
npm test -- useTranslation.test.ts
```

#### 2.3 E2E Tests

```bash
# Write E2E tests
touch tests/e2e/translation.spec.ts

# Run E2E tests
npm run test:e2e -- translation.spec.ts
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_translation_service.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

### Frontend Tests

```bash
cd textbook

# Run all tests
npm test

# Run specific test file
npm test -- TranslationControl.test.tsx

# Run E2E tests
npm run test:e2e

# Run E2E tests in headed mode (see browser)
npm run test:e2e -- --headed
```

---

## Manual Testing

### Test Scenario 1: First-Time Translation

1. Start backend: `cd backend && python -m uvicorn src.main:app --reload --port 8001`
2. Start frontend: `cd textbook && npm start -- --port 3001`
3. Open browser: `http://localhost:3001`
4. Log in with test account
5. Navigate to Chapter 1
6. Click "Translate to Urdu" button
7. Verify:
   - Loading indicator appears
   - Translation completes in <5 seconds
   - Content displays in Urdu with RTL layout
   - Technical terms remain in English (ROS 2, VSLAM, etc.)
   - Code blocks remain unchanged
   - Button text changes to "Show Original English"

### Test Scenario 2: Cached Translation

1. After completing Test Scenario 1
2. Navigate away from Chapter 1
3. Navigate back to Chapter 1
4. Verify:
   - Chapter automatically displays in Urdu (preference persisted)
   - Translation loads instantly (<500ms)
   - No loading indicator (cached)

### Test Scenario 3: Language Preference Persistence

1. Translate Chapter 1 to Urdu
2. Navigate to Chapter 2
3. Verify Chapter 2 automatically displays in Urdu
4. Click "Show Original English" on Chapter 2
5. Navigate to Chapter 3
6. Verify Chapter 3 displays in English (preference updated)

### Test Scenario 4: Unauthenticated Access

1. Log out
2. Navigate to any chapter
3. Verify:
   - No "Translate to Urdu" button visible
   - Content displays in English only

---

## Debugging

### Common Issues

#### Issue 1: OpenAI API Error

**Symptom**: Translation fails with "Translation service error"

**Solution**:
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check backend logs
tail -f backend/logs/app.log
```

#### Issue 2: Database Connection Error

**Symptom**: "Database connection failed"

**Solution**:
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check if tables exist
psql $DATABASE_URL -c "\dt"
```

#### Issue 3: Font Not Loading

**Symptom**: Urdu text displays in system font, not Noto Nastaliq Urdu

**Solution**:
```bash
# Verify fonts.css imported
grep "fonts.css" textbook/src/theme/Root.tsx

# Check browser console for font loading errors
# Open DevTools → Network → Filter by "font"

# Verify Google Fonts CDN accessible
curl -I https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu
```

#### Issue 4: RTL Layout Not Applied

**Symptom**: Urdu text displays left-to-right

**Solution**:
```bash
# Verify CSS class applied
# Open DevTools → Elements → Check for .contentUrdu class

# Verify CSS loaded
grep "direction: rtl" textbook/src/components/TranslationControl/styles.module.css

# Check for CSS conflicts
# Open DevTools → Computed → Check direction property
```

---

## Performance Testing

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test translation endpoint (10 concurrent users, 100 requests)
ab -n 100 -c 10 -H "Authorization: Bearer $JWT_TOKEN" \
  -p translate_request.json \
  -T application/json \
  http://localhost:8001/api/v1/translate

# Expected results:
# - Mean response time: <5000ms (first-time)
# - Mean response time: <500ms (cached)
# - Success rate: 100%
```

### Cache Hit Rate Monitoring

```bash
# Query cache hit rate
psql $DATABASE_URL -c "
SELECT
  COUNT(*) as total_translations,
  COUNT(DISTINCT chapter_id) as unique_chapters,
  ROUND(100.0 * COUNT(*) / COUNT(DISTINCT chapter_id), 2) as avg_requests_per_chapter
FROM translated_chapters;
"

# Expected after 1 week:
# - avg_requests_per_chapter: >10 (indicates 90%+ cache hit rate)
```

---

## Deployment

### Backend Deployment (Railway/Render)

```bash
# Set environment variables in Railway/Render dashboard:
# - DATABASE_URL (Neon Postgres)
# - OPENAI_API_KEY
# - JWT_SECRET
# - CORS_ORIGINS

# Deploy
git push railway 005-urdu-translation:main
# Or for Render:
git push render 005-urdu-translation:main

# Run migrations
railway run python scripts/migrate.py 006_add_translation_tables.sql
railway run python scripts/migrate.py 007_add_user_language_preference.sql
```

### Frontend Deployment (Vercel)

```bash
# Deploy to Vercel
vercel --prod

# Verify deployment
curl https://your-app.vercel.app
```

---

## Monitoring

### Backend Logs

```bash
# View logs
tail -f backend/logs/app.log

# Filter translation errors
grep "TRANSLATION_FAILED" backend/logs/app.log

# Monitor API latency
grep "translation_latency" backend/logs/app.log | awk '{sum+=$NF; count++} END {print sum/count}'
```

### Database Monitoring

```bash
# Check cache size
psql $DATABASE_URL -c "
SELECT
  pg_size_pretty(pg_total_relation_size('translated_chapters')) as cache_size;
"

# Check stale entries
psql $DATABASE_URL -c "
SELECT COUNT(*) as stale_count
FROM translated_chapters
WHERE updated_at < NOW() - INTERVAL '30 days';
"
```

---

## Summary

- **Setup**: 6 steps (clone, backend, database, frontend, fonts, verify)
- **Development**: TDD approach (tests first, then implementation)
- **Testing**: Unit, integration, E2E, manual scenarios
- **Debugging**: Common issues and solutions
- **Performance**: Load testing and cache monitoring
- **Deployment**: Railway/Render (backend), Vercel (frontend)
- **Monitoring**: Logs and database metrics
