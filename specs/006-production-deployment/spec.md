# Feature Specification: Production Deployment

**Feature Branch**: `006-production-deployment`
**Created**: 2026-03-02
**Status**: Draft
**Input**: User description: "Phase 5: Production Deployment - Deploy AI-Native Textbook to production with Vercel (frontend), Render (backend), and Neon Serverless Postgres. Enable CI/CD, migrate database safely, configure CORS and environment variables for production readiness without code damage."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Safe Database Migration (Priority: P1)

As a deployment engineer, I need to migrate the database from local SQLite to Neon Serverless Postgres without losing any existing user data, chat history, or translations, so that the production system has a reliable, scalable database.

**Why this priority**: Database migration is the foundation - all other deployments depend on having a working production database. Data loss would be catastrophic and unrecoverable.

**Independent Test**: Can be fully tested by migrating the database, verifying all tables exist, comparing record counts between SQLite and Neon, and testing authentication/chat/translation features against the new database.

**Acceptance Scenarios**:

1. **Given** local SQLite database with existing users, chat history, and translations, **When** migration script runs, **Then** all data appears in Neon with identical record counts and no corruption
2. **Given** Neon database is populated, **When** backend connects to Neon, **Then** authentication, chat, and translation features work identically to local environment
3. **Given** migration fails midway, **When** rollback procedure executes, **Then** system reverts to SQLite without data loss and continues functioning
4. **Given** Neon database is live, **When** schema verification runs, **Then** all 7 migrations are confirmed applied and all foreign keys are intact

---

### User Story 2 - Backend Production Deployment (Priority: P2)

As a deployment engineer, I need to deploy the FastAPI backend to Render with all environment variables, health checks, and CORS configuration, so that the backend APIs are accessible to the production frontend without errors or timeouts.

**Why this priority**: Backend must be deployed before frontend since frontend depends on backend API endpoints. Backend deployment includes critical configuration (CORS, secrets) that must be correct.

**Independent Test**: Can be fully tested by deploying backend to Render, verifying health endpoint responds, testing all API endpoints (auth, chat, translation) with production credentials, and confirming CORS allows frontend domain.

**Acceptance Scenarios**:

1. **Given** backend code is ready, **When** deployed to Render, **Then** health check endpoint returns 200 OK and service starts without errors
2. **Given** backend is deployed, **When** environment variables are configured, **Then** OpenAI, Qdrant, Neon, and JWT secrets are loaded correctly and APIs function
3. **Given** backend is running, **When** frontend makes cross-origin requests, **Then** CORS headers allow requests from production Vercel URL
4. **Given** backend has been idle for 15 minutes (Render free tier spin-down), **When** first request arrives, **Then** service wakes up within 30 seconds and responds successfully
5. **Given** deployment fails, **When** rollback is triggered, **Then** previous working version is restored within 5 minutes

---

### User Story 3 - Frontend Production Deployment (Priority: P3)

As a deployment engineer, I need to deploy the Docusaurus frontend to Vercel with correct API endpoint configuration, so that users can access the textbook, chatbot, and translation features from anywhere in the world with fast load times.

**Why this priority**: Frontend deployment comes after backend is verified working. Frontend is the user-facing component and must point to the correct production backend URL.

**Independent Test**: Can be fully tested by deploying frontend to Vercel, verifying static site loads, testing all interactive features (signup, login, chat, translation), and confirming API calls reach production backend.

**Acceptance Scenarios**:

1. **Given** frontend code is ready, **When** deployed to Vercel, **Then** static site loads in under 3 seconds globally and all pages render correctly
2. **Given** frontend is deployed, **When** API_URL environment variable is set, **Then** all API calls route to production Render backend
3. **Given** user visits production site, **When** they sign up and log in, **Then** authentication works and JWT tokens are stored correctly
4. **Given** user is authenticated, **When** they use chatbot or translation, **Then** features work identically to local environment
5. **Given** deployment fails, **When** rollback is triggered, **Then** previous working version is restored instantly via Vercel rollback

---

### User Story 4 - Automated CI/CD Pipeline (Priority: P4)

As a developer, I need automatic deployments triggered by GitHub pushes to main branch, so that future updates deploy automatically without manual intervention and preview deployments are created for pull requests.

**Why this priority**: CI/CD is important for long-term maintenance but not critical for initial launch. Manual deployment is acceptable for first production release.

**Independent Test**: Can be fully tested by pushing a small change to main branch, verifying both frontend and backend auto-deploy, and creating a PR to verify preview deployment works.

**Acceptance Scenarios**:

1. **Given** code is pushed to main branch, **When** GitHub webhook triggers, **Then** Vercel auto-deploys frontend and Render auto-deploys backend within 5 minutes
2. **Given** pull request is created, **When** Vercel processes it, **Then** preview deployment is created with unique URL for testing
3. **Given** deployment fails, **When** CI/CD detects failure, **Then** deployment stops and previous version remains live
4. **Given** tests fail in CI, **When** attempting to deploy, **Then** deployment is blocked until tests pass

---

### User Story 5 - Production Verification & Monitoring (Priority: P5)

As a deployment engineer, I need to verify all features work in production and set up monitoring, so that we can confirm successful deployment and detect issues quickly.

**Why this priority**: Verification is the final step after all deployments are complete. Monitoring is important but can be enhanced over time.

**Independent Test**: Can be fully tested by running a comprehensive checklist of all features in production environment and verifying health check endpoints are accessible.

**Acceptance Scenarios**:

1. **Given** all deployments are complete, **When** verification checklist runs, **Then** all features (auth, chat, translation, preferences) work in production
2. **Given** production is live, **When** health check endpoint is polled, **Then** backend status is reported correctly
3. **Given** user performs actions, **When** errors occur, **Then** error logs are captured and accessible for debugging
4. **Given** backend spins down, **When** frontend detects slow response, **Then** "Waking up server..." message displays to user

---

### Edge Cases

- **What happens when Neon database connection fails during migration?** System must detect connection failure, halt migration, preserve SQLite backup, and report error with clear instructions
- **What happens when environment variables are missing or incorrect?** Application must fail to start with clear error messages indicating which variables are missing, preventing partial deployment
- **What happens when CORS is misconfigured?** Frontend requests will fail with CORS errors; deployment verification must catch this before marking deployment successful
- **What happens when Render free tier spins down during active user session?** Frontend must handle timeout gracefully, show "reconnecting" message, and retry request when backend wakes up
- **What happens when deployment fails midway?** Rollback procedure must restore previous working version for both frontend and backend within 5 minutes
- **What happens when database schema in Neon doesn't match application code?** Application must detect schema mismatch on startup and refuse to start, preventing data corruption
- **What happens when OpenAI or Qdrant credentials are invalid?** Health check must detect invalid credentials and report service degradation, but authentication and basic features should still work

## Requirements *(mandatory)*

### Functional Requirements

#### Database Migration
- **FR-001**: System MUST backup local SQLite database before attempting migration to Neon
- **FR-002**: System MUST verify Neon connection is successful before starting data migration
- **FR-003**: System MUST migrate all 7 database tables (users, personalization_profiles, conversations, messages, translated_chapters, and vector metadata) without data loss
- **FR-004**: System MUST verify record counts match between SQLite and Neon after migration
- **FR-005**: System MUST test database integrity by running sample queries (user lookup, chat history retrieval, translation fetch) after migration
- **FR-006**: System MUST preserve SQLite backup for 7 days after successful migration
- **FR-007**: System MUST provide rollback procedure to revert to SQLite if Neon migration fails

#### Backend Deployment
- **FR-008**: System MUST deploy FastAPI backend to Render as a Web Service (not serverless)
- **FR-009**: System MUST configure all required environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, JWT_SECRET_KEY, FRONTEND_URL)
- **FR-010**: System MUST validate all environment variables are present on application startup
- **FR-011**: System MUST configure CORS to allow requests from production Vercel URL
- **FR-012**: System MUST expose health check endpoint at `/api/health` for monitoring
- **FR-013**: System MUST configure Render health check to poll `/api/health` every 60 seconds
- **FR-014**: System MUST include `psycopg2-binary` and `python-dotenv` in requirements.txt for Neon connectivity
- **FR-015**: System MUST log all startup errors with sufficient detail for debugging

#### Frontend Deployment
- **FR-016**: System MUST deploy Docusaurus frontend to Vercel as a static site
- **FR-017**: System MUST configure `REACT_APP_API_URL` environment variable to point to production Render backend
- **FR-018**: System MUST verify production build completes without errors before deployment
- **FR-019**: System MUST configure Vercel to serve all routes correctly (handle client-side routing)
- **FR-020**: System MUST enable Vercel automatic deployments from main branch
- **FR-021**: System MUST enable Vercel preview deployments for pull requests

#### CI/CD Pipeline
- **FR-022**: System MUST connect Render to GitHub repository for automatic backend deployments
- **FR-023**: System MUST connect Vercel to GitHub repository for automatic frontend deployments
- **FR-024**: System MUST trigger deployments only on pushes to main branch (not feature branches)
- **FR-025**: System MUST create preview deployments for pull requests to enable testing before merge
- **FR-026**: System MUST block deployments if build fails or tests fail

#### Security & Configuration
- **FR-027**: System MUST store all secrets (API keys, database URLs, JWT secrets) in platform environment variables, never in code
- **FR-028**: System MUST use GitHub Secrets for CI/CD pipeline secrets
- **FR-029**: System MUST configure Neon connection with SSL mode required (`sslmode=require`)
- **FR-030**: System MUST configure database connection pooling (pool_size=5, max_overflow=10) for Neon
- **FR-031**: System MUST validate JWT_SECRET_KEY is at least 32 characters for security

#### Rollback & Safety
- **FR-032**: System MUST provide rollback procedure for database (revert to SQLite backup)
- **FR-033**: System MUST provide rollback procedure for backend (redeploy previous Render version)
- **FR-034**: System MUST provide rollback procedure for frontend (use Vercel rollback feature)
- **FR-035**: System MUST document rollback procedures in deployment guide
- **FR-036**: System MUST test rollback procedures locally on deployment branch before production deployment

#### Verification & Monitoring
- **FR-037**: System MUST verify all features work in production before marking deployment complete
- **FR-038**: System MUST test authentication (signup, login, logout) in production
- **FR-039**: System MUST test chatbot (conversation creation, message sending, streaming) in production
- **FR-040**: System MUST test translation (request translation, view cached translation) in production
- **FR-041**: System MUST verify CORS allows cross-origin requests from frontend to backend
- **FR-042**: System MUST verify health check endpoint is accessible and returns correct status
- **FR-043**: System MUST document all production URLs (frontend, backend, database) in deployment guide

### Key Entities

- **Deployment Environment**: Represents a complete deployment (frontend URL, backend URL, database URL, status, deployment date)
- **Environment Variable**: Represents a configuration secret (name, value, platform, required/optional)
- **Migration Record**: Represents a database migration execution (migration number, status, timestamp, record counts before/after)
- **Health Check**: Represents a service health status (service name, status, last check time, error message if unhealthy)
- **Rollback Point**: Represents a snapshot for rollback (version identifier, deployment date, database backup path, git commit hash)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Database migration completes with 100% data integrity (all record counts match between SQLite and Neon)
- **SC-002**: Backend deploys successfully and health check endpoint responds within 2 seconds
- **SC-003**: Frontend deploys successfully and loads in under 3 seconds globally
- **SC-004**: All features (authentication, chatbot, translation) work identically in production as in local environment
- **SC-005**: CORS configuration allows frontend to communicate with backend without errors
- **SC-006**: Automatic deployments trigger within 5 minutes of pushing to main branch
- **SC-007**: Rollback procedures restore previous working version within 5 minutes
- **SC-008**: Backend cold start (after Render spin-down) completes within 30 seconds
- **SC-009**: Zero data loss during migration or deployment process
- **SC-010**: All environment variables are correctly configured and validated on startup
- **SC-011**: Production system handles at least 100 concurrent users without degradation
- **SC-012**: Deployment verification checklist passes 100% (all features tested and working)

## Assumptions *(optional)*

1. **GitHub Repository Access**: Deployment engineer has admin access to GitHub repository to configure webhooks and secrets
2. **Platform Accounts**: Vercel, Render, and Neon accounts are created and verified before deployment
3. **Domain Configuration**: Production domain (if custom) is configured and DNS is propagated
4. **Credentials Available**: All API keys (OpenAI, Qdrant) are available and valid for production use
5. **Local Environment Working**: Local development environment is fully functional and all tests pass before deployment
6. **Database Size**: Current SQLite database is small enough (<100MB) to migrate quickly to Neon free tier
7. **Network Access**: Deployment engineer has stable internet connection for deployment operations
8. **Backup Storage**: Sufficient local storage available for SQLite backup (at least 2x database size)
9. **Testing Time**: Sufficient time allocated for thorough production verification (at least 2 hours)
10. **Rollback Window**: Deployment occurs during low-traffic period to minimize impact if rollback needed

## Out of Scope *(optional)*

1. **Custom Domain Setup**: Using default Vercel and Render URLs; custom domain configuration is future work
2. **Advanced Monitoring**: Basic health checks only; comprehensive monitoring (Datadog, Sentry) is future work
3. **Load Balancing**: Single backend instance on Render free tier; load balancing is future work
4. **Database Replication**: Single Neon database instance; replication and failover is future work
5. **CDN Configuration**: Using Vercel's default CDN; custom CDN configuration is future work
6. **SSL Certificate Management**: Using platform-provided SSL; custom certificate management is future work
7. **Backup Automation**: Manual database backups; automated backup scheduling is future work
8. **Performance Optimization**: Basic deployment only; performance tuning (caching, compression) is future work
9. **Multi-Region Deployment**: Single region deployment; multi-region is future work
10. **Blue-Green Deployment**: Direct deployment to production; blue-green strategy is future work

## Dependencies *(optional)*

### External Dependencies
- **Vercel Platform**: Frontend hosting and CDN
- **Render Platform**: Backend hosting with persistent connections
- **Neon Platform**: Serverless Postgres database
- **GitHub**: Source code repository and CI/CD trigger
- **OpenAI API**: Required for chatbot and translation features
- **Qdrant Cloud**: Required for RAG vector search

### Internal Dependencies
- **Constitution v3.1.0**: Deployment principles (Principle XI) must be followed
- **All Migrations Applied**: Database migrations 001-007 must be applied to SQLite before migration
- **All Tests Passing**: Backend and frontend tests must pass before deployment
- **Environment Variables Documented**: `.env.example` files must be up-to-date with all required variables

### Blocking Dependencies
- **Neon Account Created**: Cannot migrate database without Neon account and connection string
- **Render Account Created**: Cannot deploy backend without Render account
- **Vercel Account Created**: Cannot deploy frontend without Vercel account
- **Production Credentials**: Cannot deploy without valid OpenAI and Qdrant production API keys

## Risks *(optional)*

### High Risk
- **Data Loss During Migration**: Mitigation: Backup SQLite before migration, verify record counts, test rollback procedure
- **Environment Variable Misconfiguration**: Mitigation: Validate all variables on startup, use `.env.example` as checklist
- **CORS Misconfiguration**: Mitigation: Test CORS in staging environment, verify with curl before frontend deployment

### Medium Risk
- **Render Cold Start Delays**: Mitigation: Implement "Waking up..." indicator in frontend, document expected behavior
- **Neon Connection Limits**: Mitigation: Configure connection pooling, monitor connection usage
- **Deployment Downtime**: Mitigation: Deploy during low-traffic period, have rollback procedure ready

### Low Risk
- **SSL Certificate Issues**: Mitigation: Use platform-provided SSL, verify HTTPS works after deployment
- **DNS Propagation Delays**: Mitigation: Use platform default URLs initially, add custom domain later
- **Build Failures**: Mitigation: Test builds locally before deployment, use CI/CD to catch failures early
