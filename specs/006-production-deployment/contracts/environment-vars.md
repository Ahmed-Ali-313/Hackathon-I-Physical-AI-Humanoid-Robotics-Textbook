# Environment Variables Reference

**Feature**: 006-production-deployment
**Date**: 2026-03-02
**Purpose**: Comprehensive documentation of all required environment variables

## Overview

This document lists all environment variables required for production deployment across Vercel (frontend), Render (backend), and local development.

---

## Backend Environment Variables (Render)

### Required Variables

| Variable | Description | Example | Validation | Where to Get |
|----------|-------------|---------|------------|--------------|
| DATABASE_URL | Neon Postgres connection string | postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require | Must start with "postgresql://" and include "sslmode=require" | Neon dashboard → Connection Details |
| OPENAI_API_KEY | OpenAI API key for chat and translation | sk-proj-xxx | Must start with "sk-" | OpenAI dashboard → API Keys |
| QDRANT_URL | Qdrant Cloud URL | https://xxx.qdrant.io | Must be valid HTTPS URL | Qdrant dashboard → Cluster URL |
| QDRANT_API_KEY | Qdrant API key | xxx | Non-empty string | Qdrant dashboard → API Keys |
| JWT_SECRET_KEY | Secret for JWT token signing | (random 32+ chars) | Length >= 32 characters | Generate: `openssl rand -hex 32` |
| FRONTEND_URL | Production Vercel URL for CORS | https://ai-native-book.vercel.app | Must be valid HTTPS URL | Vercel dashboard → Deployment URL |

### How to Set (Render Dashboard)

1. Go to Render dashboard: https://dashboard.render.com
2. Select service: **ai-native-book-backend**
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Enter key and value
6. Click **Save Changes**
7. Service will automatically redeploy

### Validation on Startup

Backend validates all required variables on startup:

```python
# backend/src/config.py
required_vars = [
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "JWT_SECRET_KEY",
    "FRONTEND_URL"
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")
```

**Startup Failure**: If any variable is missing, backend refuses to start with clear error message.

---

## Frontend Environment Variables (Vercel)

### Required Variables

| Variable | Description | Example | Validation | Where to Get |
|----------|-------------|---------|------------|--------------|
| REACT_APP_API_URL | Backend API URL | https://ai-native-book-backend.onrender.com | Must be valid HTTPS URL | Render dashboard → Service URL |

### How to Set (Vercel Dashboard)

1. Go to Vercel dashboard: https://vercel.com/dashboard
2. Select project: **ai-native-book**
3. Go to **Settings** → **Environment Variables**
4. Click **Add**
5. Enter:
   - Key: `REACT_APP_API_URL`
   - Value: `https://ai-native-book-backend.onrender.com`
   - Environments: **Production** and **Preview**
6. Click **Save**
7. Redeploy for changes to take effect

### Usage in Code

```typescript
// textbook/src/services/api.ts
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';
```

---

## Local Development Environment Variables

### Backend (.env file)

Create `backend/.env` (never commit to Git):

```bash
# Database (use SQLite for local development)
DATABASE_URL=sqlite+aiosqlite:///./ai_native_book.db

# OpenAI API
OPENAI_API_KEY=sk-proj-xxx

# Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=xxx

# JWT Secret (generate random for local)
JWT_SECRET_KEY=local-dev-secret-key-32-chars-min

# Frontend URL (local)
FRONTEND_URL=http://localhost:3001
```

### Frontend (.env file)

Create `textbook/.env` (never commit to Git):

```bash
# Backend API URL (local)
REACT_APP_API_URL=http://localhost:8001
```

### Example Files

Both directories have `.env.example` files documenting required variables:

- `backend/.env.example`
- `textbook/.env.example`

**Setup Command**:
```bash
cp backend/.env.example backend/.env
cp textbook/.env.example textbook/.env
# Then edit .env files with your actual values
```

---

## GitHub Secrets (for CI/CD)

### Required Secrets

| Secret | Description | Used By |
|--------|-------------|---------|
| OPENAI_API_KEY | OpenAI API key | GitHub Actions (if used) |
| QDRANT_API_KEY | Qdrant API key | GitHub Actions (if used) |
| DATABASE_URL | Neon connection string | GitHub Actions (if used) |

### How to Set (GitHub CLI)

```bash
gh secret set OPENAI_API_KEY --body "sk-proj-xxx"
gh secret set QDRANT_API_KEY --body "xxx"
gh secret set DATABASE_URL --body "postgresql://..."
```

### How to Set (GitHub Dashboard)

1. Go to repository: https://github.com/your-org/ai-native-book
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter name and value
5. Click **Add secret**

---

## Security Best Practices

### DO ✅

- Store secrets in platform environment variables (Render, Vercel)
- Use `.env` files for local development
- Add `.env` to `.gitignore`
- Use `.env.example` to document required variables
- Rotate secrets every 90 days
- Use strong JWT secrets (32+ characters, random)
- Use SSL for database connections (`sslmode=require`)

### DON'T ❌

- Commit `.env` files to Git
- Hardcode secrets in source code
- Share secrets via email or chat
- Use weak JWT secrets (e.g., "secret")
- Reuse secrets across environments
- Store secrets in plain text files

---

## Validation Checklist

Before deployment, verify all variables are set:

### Backend (Render)
- [ ] DATABASE_URL (starts with "postgresql://")
- [ ] OPENAI_API_KEY (starts with "sk-")
- [ ] QDRANT_URL (valid HTTPS URL)
- [ ] QDRANT_API_KEY (non-empty)
- [ ] JWT_SECRET_KEY (32+ characters)
- [ ] FRONTEND_URL (valid HTTPS URL)

### Frontend (Vercel)
- [ ] REACT_APP_API_URL (valid HTTPS URL)

### Local Development
- [ ] backend/.env exists and has all variables
- [ ] textbook/.env exists and has REACT_APP_API_URL
- [ ] .env files are in .gitignore

---

## Troubleshooting

### Backend won't start

**Error**: "Missing required environment variable: DATABASE_URL"

**Solution**: Set DATABASE_URL in Render dashboard

### Frontend can't reach backend

**Error**: "Network Error" or "CORS Error"

**Solution**:
1. Verify REACT_APP_API_URL is set in Vercel
2. Verify FRONTEND_URL is set in Render
3. Check CORS configuration in backend

### Database connection fails

**Error**: "Connection refused" or "SSL required"

**Solution**:
1. Verify DATABASE_URL includes `?sslmode=require`
2. Check Neon database is running
3. Verify connection string is correct

### OpenAI API fails

**Error**: "Invalid API key"

**Solution**:
1. Verify OPENAI_API_KEY starts with "sk-"
2. Check key is valid in OpenAI dashboard
3. Verify key has sufficient credits

---

## Environment Variable Matrix

| Variable | Local Dev | Render (Prod) | Vercel (Prod) | GitHub Secrets |
|----------|-----------|---------------|---------------|----------------|
| DATABASE_URL | SQLite | Neon | - | Optional |
| OPENAI_API_KEY | Required | Required | - | Optional |
| QDRANT_URL | Required | Required | - | Optional |
| QDRANT_API_KEY | Required | Required | - | Optional |
| JWT_SECRET_KEY | Required | Required | - | - |
| FRONTEND_URL | localhost:3001 | Vercel URL | - | - |
| REACT_APP_API_URL | localhost:8001 | - | Render URL | - |

---

## Secret Rotation Procedure

**Frequency**: Every 90 days

**Steps**:
1. Generate new secret (e.g., new OpenAI API key)
2. Add new secret to platform (Render/Vercel)
3. Verify application still works
4. Remove old secret from platform
5. Revoke old secret in provider dashboard (OpenAI/Qdrant)
6. Document rotation in history.md

**Critical**: Never remove old secret before verifying new one works!

---

## References

- Render Environment Variables: https://render.com/docs/environment-variables
- Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables
- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- OpenAI API Keys: https://platform.openai.com/api-keys
- Qdrant Cloud: https://cloud.qdrant.io
- Neon Connection Strings: https://neon.tech/docs/connect/connect-from-any-app
