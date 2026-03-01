# Quickstart: Production Deployment

**Feature**: 006-production-deployment
**Date**: 2026-03-02
**Purpose**: Step-by-step guide for deploying AI-Native Textbook to production

## Overview

This guide walks through deploying the AI-Native Textbook to production using:
- **Vercel** (frontend static site)
- **Render** (backend Web Service)
- **Neon** (Serverless Postgres database)

**Total Time**: ~60 minutes
**Prerequisites**: Admin access to GitHub repository, stable internet connection

---

## Prerequisites (5 minutes)

### 1. Create Platform Accounts

- [ ] **Neon**: https://neon.tech (sign up with GitHub)
- [ ] **Render**: https://render.com (sign up with GitHub)
- [ ] **Vercel**: https://vercel.com (sign up with GitHub)

### 2. Install Required CLIs

```bash
# Vercel CLI
npm install -g vercel

# GitHub CLI (for secrets management)
# macOS: brew install gh
# Linux: sudo apt install gh
# Windows: winget install GitHub.cli

# Verify installations
vercel --version
gh --version
```

### 3. Verify Local Environment

```bash
# Ensure you're on the deployment branch
git checkout 006-production-deployment

# Verify all tests pass
cd backend && ./venv/bin/pytest tests/ -v

# Verify frontend builds
cd ../textbook && npm run build

# Verify local servers work
# Terminal 1: cd backend && uvicorn src.main:app --reload --port 8001
# Terminal 2: cd textbook && npm start -- --port 3001
```

---

## Phase 1: Database Migration (10 minutes)

### Step 1.1: Create Neon Database

1. Go to https://console.neon.tech
2. Click **Create Project**
3. Enter project name: `ai-native-book`
4. Select region: **US East (Ohio)** (free tier)
5. Click **Create Project**
6. Copy connection string from dashboard

**Connection String Format**:
```
postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 1.2: Backup Local Database

```bash
cd /mnt/e/ai-native-book

# Create backup with timestamp
cp backend/ai_native_book.db "backend/ai_native_book.db.backup.$(date +%Y%m%d)"

# Verify backup exists
ls -lh backend/ai_native_book.db.backup.*
```

### Step 1.3: Apply Migrations to Neon

```bash
cd backend

# Temporarily update .env to use Neon
# Edit backend/.env and change DATABASE_URL to Neon connection string
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# Run migrations
python scripts/run_migrations.py

# Verify migrations applied
python -c "from src.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

**Expected Output**: List of 7 tables (users, personalization_profiles, conversations, messages, translated_chapters, etc.)

### Step 1.4: Migrate Data

```bash
# Create migration script (if not exists)
# This script will be created in /sp.tasks phase
# For now, verify schema is ready

# Test connection
python -c "from src.database import engine; print('Connection successful')"
```

### Step 1.5: Verify Data Integrity

```bash
# Compare record counts (SQLite vs Neon)
# SQLite:
sqlite3 ai_native_book.db "SELECT COUNT(*) FROM users;"

# Neon (update DATABASE_URL in .env first):
python -c "from src.database import async_session_maker; import asyncio; from sqlalchemy import select, func; from src.models.user import User; async def count(): async with async_session_maker() as session: result = await session.execute(select(func.count(User.id))); print(result.scalar()); asyncio.run(count())"
```

**Success Criteria**: Record counts match between SQLite and Neon

---

## Phase 2: Backend Deployment (15 minutes)

### Step 2.1: Prepare Backend Code

```bash
cd /mnt/e/ai-native-book

# Verify psycopg2-binary is in requirements.txt
grep "psycopg2-binary" backend/requirements.txt

# If missing, add it:
echo "psycopg2-binary>=2.9.9" >> backend/requirements.txt
echo "python-dotenv>=1.0.0" >> backend/requirements.txt

# Commit changes
git add backend/requirements.txt
git commit -m "Add Neon database dependencies"
```

### Step 2.2: Create render.yaml

```bash
# Create render.yaml in repository root
cat > render.yaml << 'EOF'
services:
  - type: web
    name: ai-native-book-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: FRONTEND_URL
        sync: false
EOF

# Commit render.yaml
git add render.yaml
git commit -m "Add Render deployment configuration"
```

### Step 2.3: Update CORS Configuration

```bash
# Edit backend/src/main.py
# Add production Vercel URL to CORS origins

# Before:
# allow_origins=["http://localhost:3001"]

# After:
# allow_origins=[
#     "http://localhost:3001",
#     "https://ai-native-book.vercel.app",  # Production
#     "https://*.vercel.app",                # Preview deployments
# ]

# Commit changes
git add backend/src/main.py
git commit -m "Add production CORS configuration"
```

### Step 2.4: Push to GitHub

```bash
git push origin 006-production-deployment
```

### Step 2.5: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **New** → **Web Service**
3. Connect GitHub repository: `ai-native-book`
4. Select branch: `006-production-deployment`
5. Render auto-detects `render.yaml` configuration
6. Click **Create Web Service**
7. Wait for initial deployment (~5 minutes)

### Step 2.6: Configure Environment Variables

1. In Render dashboard, go to **Environment** tab
2. Add each variable:

| Variable | Value | Source |
|----------|-------|--------|
| DATABASE_URL | postgresql://... | Neon dashboard |
| OPENAI_API_KEY | sk-proj-... | OpenAI dashboard |
| QDRANT_URL | https://... | Qdrant dashboard |
| QDRANT_API_KEY | ... | Qdrant dashboard |
| JWT_SECRET_KEY | (generate: `openssl rand -hex 32`) | Generate locally |
| FRONTEND_URL | https://ai-native-book.vercel.app | (will update after Vercel deployment) |

3. Click **Save Changes** (service will redeploy)

### Step 2.7: Verify Backend Deployment

```bash
# Get backend URL from Render dashboard (e.g., https://ai-native-book-backend.onrender.com)
BACKEND_URL="https://ai-native-book-backend.onrender.com"

# Test health check
curl $BACKEND_URL/api/health

# Expected response:
# {"status":"healthy","services":{"database":"healthy","openai":"healthy","qdrant":"healthy"}}

# Test authentication endpoint
curl $BACKEND_URL/api/v1/auth/health

# Expected response: 200 OK
```

**Success Criteria**: Health check returns 200 OK with all services healthy

---

## Phase 3: Frontend Deployment (10 minutes)

### Step 3.1: Update Frontend Configuration

```bash
cd /mnt/e/ai-native-book/textbook

# Update .env.example with production API URL
echo "REACT_APP_API_URL=https://ai-native-book-backend.onrender.com" > .env.example

# Commit changes
git add .env.example
git commit -m "Update frontend API URL for production"
git push origin 006-production-deployment
```

### Step 3.2: Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy from textbook directory
cd textbook
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name: ai-native-book
# - Directory: ./
# - Override settings? No

# Deployment will complete and provide URL
```

**Alternative: Deploy via Dashboard**

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Import GitHub repository: `ai-native-book`
4. Configure:
   - Framework Preset: **Docusaurus**
   - Root Directory: `textbook`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
5. Click **Deploy**

### Step 3.3: Configure Environment Variables

1. In Vercel dashboard, go to **Settings** → **Environment Variables**
2. Add variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://ai-native-book-backend.onrender.com`
   - Environments: **Production** and **Preview**
3. Click **Save**
4. Redeploy: Go to **Deployments** → Click **...** → **Redeploy**

### Step 3.4: Update Backend FRONTEND_URL

1. Go back to Render dashboard
2. Copy Vercel production URL (e.g., `https://ai-native-book.vercel.app`)
3. Update `FRONTEND_URL` environment variable in Render
4. Save changes (backend will redeploy)

### Step 3.5: Verify Frontend Deployment

```bash
# Get frontend URL from Vercel dashboard
FRONTEND_URL="https://ai-native-book.vercel.app"

# Test frontend loads
curl -I $FRONTEND_URL

# Expected response: 200 OK

# Test in browser:
# 1. Open $FRONTEND_URL
# 2. Verify site loads
# 3. Try signup/login
# 4. Test chatbot
# 5. Test translation
```

**Success Criteria**: Frontend loads, all features work

---

## Phase 4: CI/CD Setup (5 minutes)

### Step 4.1: Enable Automatic Deployments (Render)

1. Go to Render dashboard → Service settings
2. Under **Build & Deploy**, verify:
   - Auto-Deploy: **Yes**
   - Branch: `main`
3. No changes needed (already configured via render.yaml)

### Step 4.2: Enable Automatic Deployments (Vercel)

1. Go to Vercel dashboard → Project settings
2. Under **Git**, verify:
   - Production Branch: `main`
   - Auto-Deploy: **Enabled**
3. No changes needed (enabled by default)

### Step 4.3: Test CI/CD

```bash
# Merge deployment branch to main
git checkout main
git merge 006-production-deployment
git push origin main

# Watch deployments:
# - Render: https://dashboard.render.com (check logs)
# - Vercel: https://vercel.com/dashboard (check deployments)

# Verify both deploy automatically within 5 minutes
```

**Success Criteria**: Both frontend and backend auto-deploy on push to main

---

## Phase 5: Verification (15 minutes)

### Step 5.1: Run Verification Checklist

```bash
# Create verification script (will be created in /sp.tasks phase)
# For now, manual verification:

# 1. Health Check
curl https://ai-native-book-backend.onrender.com/api/health

# 2. Frontend Loads
curl -I https://ai-native-book.vercel.app

# 3. CORS Works
# Open browser console on frontend, check for CORS errors

# 4. Authentication
# Signup → Login → Verify JWT token stored

# 5. Chatbot
# Create conversation → Send message → Verify response

# 6. Translation
# Click translation button → Verify Urdu text displays

# 7. Preferences
# Change language → Verify persists across sessions
```

### Step 5.2: Document Production URLs

```bash
# Add to history.md
cat >> history.md << EOF

## 2026-03-02 - Phase 5: Production Deployment Complete

### Production URLs
- Frontend: https://ai-native-book.vercel.app
- Backend: https://ai-native-book-backend.onrender.com
- Database: Neon Serverless Postgres (ep-xxx.neon.tech)

### Deployment Status
- ✅ Database migrated (SQLite → Neon)
- ✅ Backend deployed (Render)
- ✅ Frontend deployed (Vercel)
- ✅ CI/CD enabled (GitHub → Render + Vercel)
- ✅ All features verified working

### Next Steps
- Monitor health checks for 24 hours
- Collect user feedback
- Plan performance optimizations

EOF

git add history.md
git commit -m "Document Phase 5 production deployment completion"
git push origin main
```

---

## Rollback Procedures

### Database Rollback

```bash
# Update backend/.env to use SQLite
DATABASE_URL=sqlite+aiosqlite:///./ai_native_book.db

# Restart backend (via Render dashboard or redeploy)
# SQLite backup remains valid for 7 days
```

### Backend Rollback

**Via Render Dashboard**:
1. Go to Render dashboard
2. Select service: ai-native-book-backend
3. Go to **Manual Deploy**
4. Select previous commit
5. Click **Deploy**

### Frontend Rollback

**Via Vercel Dashboard**:
1. Go to Vercel dashboard
2. Go to **Deployments**
3. Find previous successful deployment
4. Click **...** → **Promote to Production**

**Via CLI**:
```bash
vercel rollback
```

---

## Troubleshooting

### Backend won't start

**Symptom**: Render deployment fails with "Application failed to start"

**Solution**:
1. Check logs in Render dashboard
2. Verify all environment variables are set
3. Verify requirements.txt includes psycopg2-binary
4. Check DATABASE_URL format includes `?sslmode=require`

### Frontend can't reach backend

**Symptom**: "Network Error" or "CORS Error" in browser console

**Solution**:
1. Verify REACT_APP_API_URL is set in Vercel
2. Verify FRONTEND_URL is set in Render
3. Check CORS configuration in backend/src/main.py
4. Verify backend health check passes

### Database connection fails

**Symptom**: "Connection refused" or "SSL required"

**Solution**:
1. Verify DATABASE_URL includes `?sslmode=require`
2. Check Neon database is running (Neon dashboard)
3. Verify connection string is correct
4. Test connection locally first

### Cold start delays

**Symptom**: First request after 15 minutes takes 30+ seconds

**Solution**:
- This is expected behavior on Render free tier
- Frontend should show "Waking up..." message
- Consider upgrading to paid tier for always-on

---

## Post-Deployment Checklist

- [ ] All environment variables configured
- [ ] Health check endpoint responds (200 OK)
- [ ] Frontend loads in <3 seconds
- [ ] Authentication works (signup, login, logout)
- [ ] Chatbot works (create conversation, send message)
- [ ] Translation works (request translation, view Urdu)
- [ ] Preferences persist across sessions
- [ ] CORS allows cross-origin requests
- [ ] CI/CD auto-deploys on push to main
- [ ] Production URLs documented in history.md
- [ ] Rollback procedures tested (in staging)
- [ ] SQLite backup retained for 7 days

---

## Success Criteria

✅ **Database Migration**: 100% data integrity (record counts match)
✅ **Backend Deployment**: Health check responds within 2 seconds
✅ **Frontend Deployment**: Site loads in under 3 seconds globally
✅ **Feature Parity**: All features work identically to local environment
✅ **CORS Configuration**: Frontend communicates with backend without errors
✅ **CI/CD**: Automatic deployments trigger within 5 minutes
✅ **Rollback**: Procedures restore previous version within 5 minutes
✅ **Zero Data Loss**: No data lost during migration or deployment

---

## Next Steps

1. **Monitor**: Watch health checks and error logs for 24 hours
2. **Optimize**: Identify performance bottlenecks
3. **Scale**: Consider upgrading to paid tiers if needed
4. **Backup**: Set up automated database backups
5. **Monitoring**: Add comprehensive monitoring (Datadog, Sentry)

---

## References

- Neon Documentation: https://neon.tech/docs
- Render Documentation: https://render.com/docs
- Vercel Documentation: https://vercel.com/docs
- Deployment Contracts: [contracts/](./contracts/)
- Data Model: [data-model.md](./data-model.md)
- Research: [research.md](./research.md)
