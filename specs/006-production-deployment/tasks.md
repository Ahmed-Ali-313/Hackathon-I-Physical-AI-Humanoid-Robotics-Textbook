# Tasks: Production Deployment

**Input**: Design documents from `/specs/006-production-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Manual verification checklist (43 items) - no automated tests for deployment tasks

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each deployment phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `textbook/src/`
- **Configuration**: Root level (`render.yaml`, `vercel.json`)
- **Deployment scripts**: `scripts/deployment/`
- **Documentation**: `specs/006-production-deployment/`

---

## Phase 1: Setup (Prerequisites)

**Purpose**: Verify prerequisites and prepare for deployment

- [ ] T001 Verify Neon account created and database provisioned
- [ ] T002 Verify Render account created and connected to GitHub
- [ ] T003 Verify Vercel account created and connected to GitHub
- [ ] T004 [P] Install Vercel CLI: `npm install -g vercel`
- [ ] T005 [P] Install GitHub CLI and authenticate: `gh auth login`
- [ ] T006 Verify local environment: All tests pass, frontend builds successfully
- [ ] T007 Create deployment branch: `git checkout -b 006-production-deployment`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Add psycopg2-binary>=2.9.9 to backend/requirements.txt
- [ ] T009 [P] Add python-dotenv>=1.0.0 to backend/requirements.txt
- [ ] T010 Update backend/src/database.py: Add Neon connection pooling (pool_size=5, max_overflow=10, pool_pre_ping=True)
- [ ] T011 Update backend/src/config.py: Add environment variable validation on startup
- [ ] T012 Update backend/src/main.py: Add production CORS origins (Vercel URL, *.vercel.app)
- [ ] T013 Update backend/.env.example: Document all 6 required environment variables
- [ ] T014 [P] Update textbook/.env.example: Document REACT_APP_API_URL
- [ ] T015 Create render.yaml in repository root with Web Service configuration
- [ ] T016 [P] Create scripts/deployment/ directory for deployment automation
- [ ] T017 Commit foundational changes: `git add . && git commit -m "Add production deployment configuration"`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Safe Database Migration (Priority: P1) 🎯 MVP

**Goal**: Migrate database from SQLite to Neon with zero data loss and rollback capability

**Independent Test**: Run migration script, verify record counts match, test authentication/chat/translation against Neon, execute rollback procedure

### Implementation for User Story 1

- [ ] T018 [US1] Create Neon database project via Neon console (region: US East Ohio)
- [ ] T019 [US1] Copy Neon connection string from dashboard (format: postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require)
- [ ] T020 [US1] Create SQLite backup: `cp backend/ai_native_book.db backend/ai_native_book.db.backup.$(date +%Y%m%d)`
- [ ] T021 [US1] Create scripts/deployment/migrate-to-neon.sh: Database migration script with record count verification
- [ ] T022 [US1] Update backend/.env temporarily: Set DATABASE_URL to Neon connection string
- [ ] T023 [US1] Run migrations on Neon: `cd backend && python scripts/run_migrations.py`
- [ ] T024 [US1] Verify all 7 tables exist in Neon: `python -c "from src.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"`
- [ ] T025 [US1] Export SQLite data to JSON: Create Python script to export all tables
- [ ] T026 [US1] Import data to Neon: Create Python script to import JSON data with transaction safety
- [ ] T027 [US1] Verify record counts match: Compare SQLite vs Neon for all 7 tables
- [ ] T028 [US1] Test authentication against Neon: Signup, login, verify JWT tokens work
- [ ] T029 [US1] Test chat history against Neon: Create conversation, send message, verify retrieval
- [ ] T030 [US1] Test translation against Neon: Request translation, verify cached translation retrieval
- [ ] T031 [US1] Create scripts/deployment/rollback-database.sh: Rollback procedure (revert DATABASE_URL to SQLite)
- [ ] T032 [US1] Test rollback procedure: Execute rollback, verify system works with SQLite
- [ ] T033 [US1] Document migration results: Record counts, duration, any issues in history.md

**Checkpoint**: Database migration complete - backend can now be deployed to Render

---

## Phase 4: User Story 2 - Backend Production Deployment (Priority: P2)

**Goal**: Deploy FastAPI backend to Render with environment variables, health checks, and CORS

**Independent Test**: Deploy to Render, verify health endpoint responds, test all APIs with production credentials, confirm CORS works

### Implementation for User Story 2

- [ ] T034 [US2] Push deployment branch to GitHub: `git push origin 006-production-deployment`
- [ ] T035 [US2] Connect Render to GitHub repository via Render dashboard
- [ ] T036 [US2] Select branch 006-production-deployment in Render (render.yaml auto-detected)
- [ ] T037 [US2] Click "Create Web Service" and wait for initial deployment (~5 minutes)
- [ ] T038 [US2] Configure DATABASE_URL in Render dashboard Environment tab (Neon connection string)
- [ ] T039 [P] [US2] Configure OPENAI_API_KEY in Render dashboard Environment tab
- [ ] T040 [P] [US2] Configure QDRANT_URL in Render dashboard Environment tab
- [ ] T041 [P] [US2] Configure QDRANT_API_KEY in Render dashboard Environment tab
- [ ] T042 [US2] Generate JWT_SECRET_KEY: `openssl rand -hex 32` and configure in Render
- [ ] T043 [US2] Configure FRONTEND_URL in Render (placeholder: https://ai-native-book.vercel.app, update after Vercel deployment)
- [ ] T044 [US2] Save environment variables (service will redeploy automatically)
- [ ] T045 [US2] Copy backend URL from Render dashboard (e.g., https://ai-native-book-backend.onrender.com)
- [ ] T046 [US2] Test health check endpoint: `curl https://ai-native-book-backend.onrender.com/api/health`
- [ ] T047 [US2] Verify health check returns 200 OK with all services healthy
- [ ] T048 [US2] Test authentication endpoint: `curl https://ai-native-book-backend.onrender.com/api/v1/auth/health`
- [ ] T049 [US2] Test CORS configuration: Verify CORS headers allow Vercel domain (use curl with Origin header)
- [ ] T050 [US2] Document backend URL in specs/006-production-deployment/deployment-urls.md
- [ ] T051 [US2] Test rollback procedure: Redeploy previous commit via Render dashboard

**Checkpoint**: Backend deployed and verified - frontend can now be deployed

---

## Phase 5: User Story 3 - Frontend Production Deployment (Priority: P3)

**Goal**: Deploy Docusaurus frontend to Vercel with correct API endpoint configuration

**Independent Test**: Deploy to Vercel, verify site loads, test all features (signup, login, chat, translation), confirm API calls reach backend

### Implementation for User Story 3

- [ ] T052 [US3] Update textbook/.env.example: Set REACT_APP_API_URL to Render backend URL
- [ ] T053 [US3] Commit frontend configuration: `git add textbook/.env.example && git commit -m "Update frontend API URL for production"`
- [ ] T054 [US3] Push to GitHub: `git push origin 006-production-deployment`
- [ ] T055 [US3] Connect Vercel to GitHub repository via Vercel dashboard
- [ ] T056 [US3] Configure project: Framework=Docusaurus, Root Directory=textbook, Build Command=npm run build (auto-detected)
- [ ] T057 [US3] Click "Deploy" and wait for deployment (~5 minutes)
- [ ] T058 [US3] Configure REACT_APP_API_URL in Vercel Environment Variables (value: Render backend URL, environments: Production + Preview)
- [ ] T059 [US3] Redeploy frontend: Go to Deployments → Click "..." → "Redeploy"
- [ ] T060 [US3] Copy frontend URL from Vercel dashboard (e.g., https://ai-native-book.vercel.app)
- [ ] T061 [US3] Update FRONTEND_URL in Render dashboard to Vercel production URL
- [ ] T062 [US3] Wait for Render backend to redeploy with updated CORS configuration
- [ ] T063 [US3] Test frontend loads: `curl -I https://ai-native-book.vercel.app` (expect 200 OK)
- [ ] T064 [US3] Test frontend in browser: Verify site loads in <3 seconds
- [ ] T065 [US3] Test signup flow: Create new account, verify JWT token stored
- [ ] T066 [US3] Test login flow: Login with credentials, verify authentication works
- [ ] T067 [US3] Test chatbot: Create conversation, send message, verify response
- [ ] T068 [US3] Test translation: Click translation button, verify Urdu text displays
- [ ] T069 [US3] Test preferences: Change language, verify persists across sessions
- [ ] T070 [US3] Document frontend URL in specs/006-production-deployment/deployment-urls.md
- [ ] T071 [US3] Test rollback procedure: Execute `vercel rollback` via CLI or dashboard

**Checkpoint**: Frontend deployed and verified - CI/CD can now be enabled

---

## Phase 6: User Story 4 - Automated CI/CD Pipeline (Priority: P4)

**Goal**: Enable automatic deployments from GitHub for both frontend and backend

**Independent Test**: Push small change to main, verify auto-deploy, create PR to verify preview deployment

### Implementation for User Story 4

- [ ] T072 [US4] Verify Render auto-deploy enabled: Check Render dashboard → Build & Deploy → Auto-Deploy=Yes, Branch=main
- [ ] T073 [US4] Verify Vercel auto-deploy enabled: Check Vercel dashboard → Git → Production Branch=main, Auto-Deploy=Enabled
- [ ] T074 [US4] Merge deployment branch to main: `git checkout main && git merge 006-production-deployment`
- [ ] T075 [US4] Push to main: `git push origin main`
- [ ] T076 [US4] Monitor Render deployment: Watch logs in Render dashboard (expect deployment within 5 minutes)
- [ ] T077 [US4] Monitor Vercel deployment: Watch deployments in Vercel dashboard (expect deployment within 5 minutes)
- [ ] T078 [US4] Verify both deployments complete successfully
- [ ] T079 [US4] Test CI/CD: Make small change (e.g., update README), commit, push to main
- [ ] T080 [US4] Verify automatic deployments trigger for both frontend and backend
- [ ] T081 [US4] Create test PR: Create feature branch, make change, open PR
- [ ] T082 [US4] Verify Vercel preview deployment created with unique URL
- [ ] T083 [US4] Test preview deployment: Verify preview site works correctly
- [ ] T084 [US4] Close test PR and verify preview deployment is deleted
- [ ] T085 [US4] Document CI/CD configuration in specs/006-production-deployment/ci-cd-setup.md

**Checkpoint**: CI/CD enabled - production verification can now begin

---

## Phase 7: User Story 5 - Production Verification & Monitoring (Priority: P5)

**Goal**: Verify all features work in production and document deployment

**Independent Test**: Run comprehensive verification checklist, test all features, verify health checks

### Implementation for User Story 5

- [ ] T086 [US5] Create scripts/deployment/verify-deployment.sh: Automated verification script
- [ ] T087 [US5] Verify health check endpoint: `curl https://ai-native-book-backend.onrender.com/api/health` (expect 200 OK)
- [ ] T088 [US5] Verify frontend loads: `curl -I https://ai-native-book.vercel.app` (expect 200 OK, <3s)
- [ ] T089 [US5] Verify CORS works: Check browser console for CORS errors (expect none)
- [ ] T090 [US5] Verify authentication: Signup → Login → Logout (expect all work)
- [ ] T091 [US5] Verify chatbot: Create conversation → Send message → Verify streaming response
- [ ] T092 [US5] Verify translation: Request translation → Verify Urdu text displays → Verify caching works
- [ ] T093 [US5] Verify preferences: Change language → Verify persists across sessions
- [ ] T094 [US5] Verify database connection: Check Render logs for successful Neon connections
- [ ] T095 [US5] Verify environment variables: Check Render logs for successful variable loading
- [ ] T096 [US5] Test cold start behavior: Wait 15 minutes, make request, verify 30-second wake-up
- [ ] T097 [US5] Verify error logging: Trigger error, check Render logs for error capture
- [ ] T098 [US5] Document production URLs in history.md (frontend, backend, database)
- [ ] T099 [US5] Document deployment completion date and status in history.md
- [ ] T100 [US5] Create deployment summary: Record migration results, deployment times, any issues
- [ ] T101 [US5] Verify rollback procedures documented: Database, backend, frontend rollback steps
- [ ] T102 [US5] Schedule 24-hour monitoring: Monitor health checks and error logs

**Checkpoint**: Production deployment complete and verified

---

## Phase 8: Polish & Documentation

**Purpose**: Final documentation and cleanup

- [ ] T103 Update history.md: Add Phase 5 deployment completion entry with production URLs
- [ ] T104 [P] Create deployment guide: Document step-by-step deployment procedure for future reference
- [ ] T105 [P] Document troubleshooting: Common issues and solutions in specs/006-production-deployment/troubleshooting.md
- [ ] T106 Tag release: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] T107 Archive SQLite backup: Move backup to safe location, retain for 7 days

---

## Dependencies

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
                  Phase 3 (US1: Database Migration) ← MUST complete first
                      ↓
                  Phase 4 (US2: Backend Deployment) ← Depends on US1
                      ↓
                  Phase 5 (US3: Frontend Deployment) ← Depends on US2
                      ↓
                  Phase 6 (US4: CI/CD Pipeline) ← Depends on US3
                      ↓
                  Phase 7 (US5: Verification) ← Depends on US4
                      ↓
                  Phase 8 (Polish)
```

**Critical Path**: US1 → US2 → US3 → US4 → US5 (sequential, no parallelization between stories)

**Within-Story Parallelization**:
- US1: Tasks T025-T026 (export/import) can be prepared in parallel
- US2: Tasks T039-T041 (environment variables) can be configured in parallel
- US3: Tasks T064-T069 (feature testing) can be tested in parallel
- US5: Tasks T090-T093 (feature verification) can be verified in parallel

---

## Parallel Execution Examples

### Phase 2 (Foundational)
```bash
# Can run in parallel:
- T009: Add python-dotenv (different line in requirements.txt)
- T014: Update textbook/.env.example (different directory)
- T016: Create scripts/deployment/ (different directory)
```

### Phase 4 (US2: Backend Deployment)
```bash
# Can run in parallel after T038:
- T039: Configure OPENAI_API_KEY
- T040: Configure QDRANT_URL
- T041: Configure QDRANT_API_KEY
```

### Phase 7 (US5: Verification)
```bash
# Can run in parallel after T089:
- T090: Test authentication
- T091: Test chatbot
- T092: Test translation
- T093: Test preferences
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**User Story 1 only**: Safe Database Migration
- Provides production-ready database (Neon)
- Enables backend to connect to scalable database
- Validates migration and rollback procedures
- Deliverable: Working Neon database with all data migrated

### Incremental Delivery
1. **Sprint 1**: US1 (Database Migration) - 2 hours
2. **Sprint 2**: US2 (Backend Deployment) - 2 hours
3. **Sprint 3**: US3 (Frontend Deployment) - 1.5 hours
4. **Sprint 4**: US4 (CI/CD Pipeline) - 1 hour
5. **Sprint 5**: US5 (Verification) - 1.5 hours

**Total Estimated Time**: 8 hours (includes buffer for troubleshooting)

### Risk Mitigation
- **High Risk (US1)**: Database migration with data loss potential
  - Mitigation: Backup before migration, verify record counts, test rollback
- **Medium Risk (US2)**: Environment variable misconfiguration
  - Mitigation: Validate on startup, fail fast with clear errors
- **Low Risk (US3-US5)**: Configuration issues
  - Mitigation: Test in browser, verify CORS, rollback if needed

---

## Task Summary

**Total Tasks**: 107
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (US1 - Database Migration): 16 tasks
- Phase 4 (US2 - Backend Deployment): 18 tasks
- Phase 5 (US3 - Frontend Deployment): 20 tasks
- Phase 6 (US4 - CI/CD Pipeline): 14 tasks
- Phase 7 (US5 - Verification): 17 tasks
- Phase 8 (Polish): 5 tasks

**Parallel Opportunities**: 15 tasks marked with [P]

**Independent Test Criteria**:
- US1: Migration complete, record counts match, rollback tested
- US2: Health check responds, APIs work, CORS configured
- US3: Site loads, features work, API calls reach backend
- US4: Auto-deploy works, preview deployments created
- US5: All features verified, monitoring enabled

**Format Validation**: ✅ All 107 tasks follow checklist format with checkbox, ID, optional [P]/[Story] labels, and file paths
