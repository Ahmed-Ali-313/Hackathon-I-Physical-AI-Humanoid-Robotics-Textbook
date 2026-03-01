# Research: Production Deployment Best Practices

**Feature**: 006-production-deployment
**Date**: 2026-03-02
**Purpose**: Document platform-specific best practices and deployment decisions

## Overview

This research consolidates best practices for deploying a FastAPI + Docusaurus application to production using Vercel (frontend), Render (backend), and Neon (database). Focus on safety, zero data loss, and rollback capabilities.

---

## 1. Neon Migration Best Practices

### Decision: Use pg_dump/pg_restore for SQLite → Postgres Migration

**Rationale**:
- SQLite and PostgreSQL have different data types and constraints
- Direct SQL dump may cause type mismatches
- Python-based migration script provides better control and validation

**Migration Strategy**:
1. Export SQLite data to JSON/CSV using Python script
2. Transform data to match PostgreSQL types
3. Import to Neon using SQLAlchemy with transactions
4. Verify record counts and foreign key integrity

**Alternatives Considered**:
- `sqlite3 .dump | psql`: Rejected due to SQL dialect incompatibilities
- Manual CSV export/import: Rejected due to lack of transaction safety
- Third-party tools (pgloader): Rejected to minimize dependencies

### Decision: Connection Pooling Configuration

**Configuration**:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # Max 5 connections in pool
    max_overflow=10,      # Allow 10 additional connections
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

**Rationale**:
- Neon free tier supports up to 100 concurrent connections
- pool_size=5 is sufficient for Render free tier (single instance)
- max_overflow=10 handles traffic spikes
- pool_pre_ping prevents stale connection errors
- pool_recycle prevents long-lived connection issues

**Alternatives Considered**:
- Larger pool (20+): Rejected due to free tier limits and single instance
- No pooling: Rejected due to connection overhead

### Decision: SSL Mode Required

**Configuration**: `sslmode=require` in connection string

**Rationale**:
- Neon requires SSL for all connections
- Prevents man-in-the-middle attacks
- Standard practice for cloud databases

---

## 2. Render Deployment Configuration

### Decision: Web Service (Not Serverless)

**Rationale**:
- FastAPI backend has long-running processes (streaming chat, translation)
- Serverless functions have timeout limits (10-60 seconds)
- Web Service provides persistent connections to Qdrant and Neon
- Free tier includes 750 hours/month (sufficient for development)

**Alternatives Considered**:
- Serverless functions: Rejected due to timeout limits for streaming
- Docker deployment: Rejected to simplify initial deployment

### Decision: Health Check Configuration

**Configuration**:
```yaml
healthCheckPath: /api/health
healthCheckInterval: 60  # seconds
healthCheckTimeout: 10   # seconds
```

**Rationale**:
- 60-second interval balances monitoring and resource usage
- 10-second timeout allows for cold start delays
- `/api/health` endpoint returns service status

**Health Check Response Format**:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "openai": "healthy",
    "qdrant": "healthy"
  }
}
```

### Decision: Automatic Deployment from GitHub

**Configuration**: Connect Render to GitHub repository, auto-deploy on push to `main`

**Rationale**:
- Eliminates manual deployment steps
- Ensures production matches main branch
- Preview deployments not needed for backend (Vercel handles frontend previews)

---

## 3. Vercel Deployment Configuration

### Decision: Static Site Generation (SSG)

**Rationale**:
- Docusaurus generates static HTML/CSS/JS
- No server-side rendering needed
- Optimal performance with CDN distribution
- Free tier sufficient for static sites

**Build Configuration**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "installCommand": "npm install"
}
```

### Decision: Environment Variable for API URL

**Configuration**: `REACT_APP_API_URL` set in Vercel dashboard

**Rationale**:
- Allows different API URLs for preview vs production
- No hardcoded URLs in code
- Standard React environment variable pattern

**Alternatives Considered**:
- Hardcoded URL: Rejected due to inflexibility
- Runtime configuration: Rejected due to SSG (no runtime)

### Decision: Preview Deployments for PRs

**Configuration**: Enable automatic preview deployments

**Rationale**:
- Allows testing changes before merging to main
- Each PR gets unique URL
- No impact on production deployment

---

## 4. CORS Configuration

### Decision: Explicit Origin Whitelisting

**Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",           # Local development
        "https://ai-native-book.vercel.app",  # Production
        "https://*.vercel.app",            # Preview deployments
    ],
    allow_credentials=True,  # Required for JWT cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Rationale**:
- Explicit whitelist prevents unauthorized access
- Wildcard for Vercel preview deployments (*.vercel.app)
- allow_credentials=True required for JWT authentication
- Specific methods reduce attack surface

**Alternatives Considered**:
- allow_origins=["*"]: Rejected due to security risk
- No CORS: Rejected due to browser same-origin policy

### Decision: Preflight Request Handling

**Rationale**:
- FastAPI CORS middleware handles OPTIONS requests automatically
- No additional configuration needed
- Supports complex requests (custom headers, credentials)

---

## 5. GitHub Secrets Management

### Decision: Use GitHub CLI for Secret Management

**Commands**:
```bash
gh secret set OPENAI_API_KEY --body "sk-proj-xxx"
gh secret set QDRANT_API_KEY --body "xxx"
gh secret set DATABASE_URL --body "postgresql://..."
```

**Rationale**:
- GitHub CLI provides secure secret storage
- Secrets encrypted at rest
- Available to GitHub Actions (if used)
- Easier than manual dashboard entry

**Alternatives Considered**:
- Manual dashboard entry: Rejected due to tedious process
- .env file in repository: Rejected due to security risk

### Decision: Secret Rotation Policy

**Policy**: Rotate secrets every 90 days

**Rationale**:
- Industry standard for API key rotation
- Reduces risk of compromised credentials
- Neon, Render, Vercel support secret updates without downtime

---

## 6. Backup and Rollback Strategy

### Decision: 7-Day SQLite Backup Retention

**Rationale**:
- Provides safety net for migration issues
- 7 days sufficient to detect and resolve problems
- Local storage cost negligible (<100MB)

**Backup Command**:
```bash
cp ai_native_book.db "ai_native_book.db.backup.$(date +%Y%m%d)"
```

### Decision: Git-Based Rollback for Code

**Rationale**:
- Render and Vercel support redeploying previous commits
- Git provides complete history and audit trail
- No need for separate backup mechanism

**Rollback Commands**:
```bash
# Render: Redeploy previous commit via dashboard
# Vercel: vercel rollback (via CLI or dashboard)
```

### Decision: Database Rollback via Connection String

**Rationale**:
- Fastest rollback method (update env var, restart)
- No data migration needed
- SQLite backup remains valid for 7 days

---

## 7. Deployment Verification

### Decision: Automated Verification Script

**Script**: `scripts/deployment/verify-deployment.sh`

**Checks**:
1. Health check endpoint responds (200 OK)
2. Frontend loads (200 OK, <3s)
3. CORS allows frontend domain
4. Authentication works (signup, login)
5. Chatbot works (create conversation, send message)
6. Translation works (request translation)
7. Database connection valid
8. Environment variables loaded

**Rationale**:
- Automated checks reduce human error
- Comprehensive coverage of all features
- Fast feedback (completes in <2 minutes)

---

## 8. Cold Start Handling

### Decision: Frontend "Waking Up" Indicator

**Implementation**:
- Detect slow response (>5 seconds)
- Show "Waking up server..." message
- Retry request after 30 seconds

**Rationale**:
- Render free tier spins down after 15 minutes idle
- Cold start takes 20-30 seconds
- User-friendly message manages expectations

**Alternatives Considered**:
- Keep-alive pings: Rejected due to free tier hour limits
- Upgrade to paid tier: Deferred to future

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Migration Method | Python script with SQLAlchemy | Type safety, transaction control |
| Connection Pooling | pool_size=5, max_overflow=10 | Balances performance and free tier limits |
| Backend Platform | Render Web Service | Supports long-running processes |
| Frontend Platform | Vercel Static Site | Optimal for Docusaurus SSG |
| Database Platform | Neon Serverless Postgres | Serverless, free tier, SSL required |
| CORS Strategy | Explicit origin whitelist | Security best practice |
| Secret Management | GitHub CLI + Platform dashboards | Secure, auditable |
| Backup Retention | 7 days (SQLite) | Safety net for migration issues |
| Rollback Strategy | Git-based + connection string | Fast, reliable |
| Verification | Automated script | Comprehensive, fast feedback |

---

## References

- Neon Documentation: https://neon.tech/docs
- Render Documentation: https://render.com/docs
- Vercel Documentation: https://vercel.com/docs
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- SQLAlchemy Connection Pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
