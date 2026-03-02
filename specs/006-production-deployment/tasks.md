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

- [ ] T001 Update GitHub repository name to "Hackathon I: Physical AI & Humanoid Robotics Textbook"
- [ ] T002 Update GitHub repository description: "AI-Native technical textbook on Physical AI and Humanoid Robotics featuring an integrated RAG chatbot with OpenAI, Urdu translation support, and user authentication. Built with Docusaurus (frontend), FastAPI (backend), Qdrant (vector search), and Neon Postgres. Deployed on Vercel and Render."
- [ ] T003 Verify Neon account created and database provisioned
- [ ] T004 Verify Render account created and connected to GitHub
- [ ] T005 Verify Vercel account created and connected to GitHub
- [ ] T006 [P] Install Vercel CLI: `npm install -g vercel`
- [ ] T007 [P] Install GitHub CLI and authenticate: `gh auth login`
- [ ] T008 Verify local environment: All tests pass, frontend builds successfully
- [ ] T009 Verify current branch is 006-production-deployment: `git branch --show-current`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Add psycopg2-binary>=2.9.9 to backend/requirements.txt
- [ ] T011 [P] Add python-dotenv>=1.0.0 to backend/requirements.txt
- [ ] T012 Update backend/src/database.py: Add Neon connection pooling (pool_size=5, max_overflow=10, pool_pre_ping=True)
- [ ] T013 Update backend/src/config.py: Add environment variable validation on startup (including JWT_SECRET_KEY length >=32 chars) - handles edge case: missing/incorrect env vars
- [ ] T014 Update backend/src/main.py: Add production CORS origins (Vercel URL, *.vercel.app)
- [ ] T015 Update backend/.env.example: Document all 6 required environment variables
- [ ] T016 [P] Update textbook/.env.example: Document REACT_APP_API_URL
- [ ] T017 Create render.yaml in repository root with Web Service configuration
- [ ] T018 [P] Create scripts/deployment/ directory for deployment automation
- [ ] T019 Commit foundational changes: `git add . && git commit -m "Add production deployment configuration"`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Safe Database Migration (Priority: P1) 🎯 MVP

**Goal**: Migrate database from SQLite to Neon with zero data loss and rollback capability

**Independent Test**: Run migration script, verify record counts match, test authentication/chat/translation against Neon, execute rollback procedure

### Implementation for User Story 1

- [ ] T020 [US1] Create Neon database project via Neon console (region: US East Ohio)
- [ ] T021 [US1] Copy Neon connection string from dashboard (format: postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require) - handles edge case: Neon connection failure detection
- [ ] T022 [US1] Create SQLite backup: `cp backend/ai_native_book.db backend/ai_native_book.db.backup.$(date +%Y%m%d)`
- [ ] T023 [US1] Create scripts/deployment/migrate-to-neon.sh: Database migration script with record count verification
- [ ] T024 [US1] Update backend/.env temporarily: Set DATABASE_URL to Neon connection string
- [ ] T025 [US1] Run migrations on Neon: `cd backend && python scripts/run_migrations.py`
- [ ] T026 [US1] Verify all 7 tables exist in Neon: `python -c "from src.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"` - handles edge case: database schema mismatch
- [ ] T027 [US1] Export SQLite data to JSON: Create Python script to export all tables
- [ ] T028 [US1] Import data to Neon: Create Python script to import JSON data with transaction safety
- [ ] T029 [US1] Verify record counts match: Compare SQLite vs Neon for all 7 tables
- [ ] T030 [US1] Test authentication against Neon: Signup, login, verify JWT tokens work
- [ ] T031 [US1] Test chat history against Neon: Create conversation, send message, verify retrieval
- [ ] T032 [US1] Test translation against Neon: Request translation, verify cached translation retrieval
- [ ] T033 [US1] Create scripts/deployment/rollback-database.sh: Rollback procedure (revert DATABASE_URL to SQLite) - handles edge case: deployment fails midway
- [ ] T034 [US1] Test rollback procedure: Execute rollback, verify system works with SQLite
- [ ] T035 [US1] Document migration results: Record counts, duration, any issues in history.md

**Checkpoint**: Database migration complete - backend can now be deployed to Render

---

## Phase 4: User Story 2 - Backend Production Deployment (Priority: P2)

**Goal**: Deploy FastAPI backend to Render with environment variables, health checks, and CORS

**Independent Test**: Deploy to Render, verify health endpoint responds, test all APIs with production credentials, confirm CORS works

### Implementation for User Story 2

- [x] T036 [US2] Push deployment branch to GitHub: `git push origin 006-production-deployment`
- [x] T037 [US2] Connect Render to GitHub repository via Render dashboard
- [x] T038 [US2] Select branch 006-production-deployment in Render (render.yaml auto-detected)
- [x] T039 [US2] Click "Create Web Service" and wait for initial deployment (~5 minutes)
- [x] T040 [US2] Configure DATABASE_URL in Render dashboard Environment tab (Neon connection string)
- [x] T041 [P] [US2] Configure OPENAI_API_KEY in Render dashboard Environment tab
- [x] T042 [P] [US2] Configure QDRANT_URL in Render dashboard Environment tab
- [x] T043 [P] [US2] Configure QDRANT_API_KEY in Render dashboard Environment tab
- [x] T044 [US2] Generate JWT_SECRET_KEY: `openssl rand -hex 32` and configure in Render
- [x] T045 [US2] Configure FRONTEND_URL in Render (placeholder: https://ai-native-book.vercel.app, update after Vercel deployment)
- [x] T046 [US2] Save environment variables (service will redeploy automatically)
- [x] T047 [US2] Copy backend URL from Render dashboard (e.g., https://ai-native-book-backend.onrender.com)
- [x] T048 [US2] Test health check endpoint: `curl https://ai-native-book-backend.onrender.com/api/health`
- [x] T049 [US2] Verify health check returns 200 OK with all services healthy
- [x] T050 [US2] Test authentication endpoint: `curl https://ai-native-book-backend.onrender.com/api/v1/auth/health`
- [x] T051 [US2] Test CORS configuration: Verify CORS headers allow Vercel domain (use curl with Origin header) - handles edge case: CORS misconfiguration
- [x] T052 [US2] Document backend URL in specs/006-production-deployment/deployment-urls.md
- [ ] T053 [US2] Test rollback procedure: Redeploy previous commit via Render dashboard

**Checkpoint**: Backend deployed and verified - frontend can now be deployed

---

## Phase 5: User Story 3 - Frontend Production Deployment (Priority: P3)

**Goal**: Deploy Docusaurus frontend to Vercel with correct API endpoint configuration

**Independent Test**: Deploy to Vercel, verify site loads, test all features (signup, login, chat, translation), confirm API calls reach backend

### Implementation for User Story 3

- [ ] T054 [US3] Update textbook/.env.example: Set REACT_APP_API_URL to Render backend URL
- [ ] T055 [US3] Commit frontend configuration: `git add textbook/.env.example && git commit -m "Update frontend API URL for production"`
- [ ] T056 [US3] Push to GitHub: `git push origin 006-production-deployment`
- [ ] T057 [US3] Connect Vercel to GitHub repository via Vercel dashboard
- [ ] T058 [US3] Configure project: Framework=Docusaurus, Root Directory=textbook, Build Command=npm run build (auto-detected)
- [ ] T058a [US3] Verify Vercel client-side routing configuration: Docusaurus handles routing automatically, confirm no additional vercel.json rewrites needed
- [ ] T059 [US3] Click "Deploy" and wait for deployment (~5 minutes)
- [ ] T060 [US3] Configure REACT_APP_API_URL in Vercel Environment Variables (value: Render backend URL, environments: Production + Preview)
- [ ] T061 [US3] Redeploy frontend: Go to Deployments → Click "..." → "Redeploy"
- [ ] T062 [US3] Copy frontend URL from Vercel dashboard (e.g., https://ai-native-book.vercel.app)
- [ ] T063 [US3] Update FRONTEND_URL in Render dashboard to Vercel production URL
- [ ] T064 [US3] Wait for Render backend to redeploy with updated CORS configuration
- [ ] T065 [US3] Test frontend loads: `curl -I https://ai-native-book.vercel.app` (expect 200 OK)
- [ ] T066 [US3] Test frontend in browser: Verify site loads in <3 seconds
- [ ] T067 [US3] Test signup flow: Create new account, verify JWT token stored
- [ ] T068 [US3] Test login flow: Login with credentials, verify authentication works
- [ ] T069 [US3] Test chatbot: Create conversation, send message, verify response
- [ ] T070 [US3] Test translation: Click translation button, verify Urdu text displays
- [ ] T071 [US3] Test preferences: Change language, verify persists across sessions
- [ ] T072 [US3] Document frontend URL in specs/006-production-deployment/deployment-urls.md
- [ ] T073 [US3] Test rollback procedure: Execute `vercel rollback` via CLI or dashboard

**Checkpoint**: Frontend deployed and verified - CI/CD can now be enabled

---

## Phase 6: User Story 4 - Automated CI/CD Pipeline (Priority: P4)

**Goal**: Enable automatic deployments from GitHub for both frontend and backend

**Independent Test**: Push small change to main, verify auto-deploy, create PR to verify preview deployment

### Implementation for User Story 4

- [ ] T074 [US4] Verify Render auto-deploy enabled: Check Render dashboard → Build & Deploy → Auto-Deploy=Yes, Branch=main
- [ ] T074a [US4] Verify Render blocks failed builds: Confirm "Auto-Deploy" setting includes build failure detection (default behavior)
- [ ] T075 [US4] Verify Vercel auto-deploy enabled: Check Vercel dashboard → Git → Production Branch=main, Auto-Deploy=Enabled
- [ ] T075a [US4] Verify Vercel blocks failed builds: Confirm deployment settings block on build errors (default behavior)
- [ ] T076 [US4] Merge deployment branch to main: `git checkout main && git merge 006-production-deployment`
- [ ] T077 [US4] Push to main: `git push origin main`
- [ ] T078 [US4] Monitor Render deployment: Watch logs in Render dashboard (expect deployment within 5 minutes)
- [ ] T079 [US4] Monitor Vercel deployment: Watch deployments in Vercel dashboard (expect deployment within 5 minutes)
- [ ] T080 [US4] Verify both deployments complete successfully
- [ ] T081 [US4] Test CI/CD: Make small change (e.g., update README), commit, push to main
- [ ] T082 [US4] Verify automatic deployments trigger for both frontend and backend
- [ ] T083 [US4] Create test PR: Create feature branch, make change, open PR
- [ ] T084 [US4] Verify Vercel preview deployment created with unique URL
- [ ] T085 [US4] Test preview deployment: Verify preview site works correctly
- [ ] T086 [US4] Close test PR and verify preview deployment is deleted
- [ ] T086a [US4] Sync environment variables to GitHub Secrets: Use `gh secret set` for CI/CD pipeline access (if needed for future GitHub Actions)
- [ ] T087 [US4] Document CI/CD configuration in specs/006-production-deployment/ci-cd-setup.md

**Checkpoint**: CI/CD enabled - production verification can now begin

---

## Phase 7: User Story 5 - Production Verification & Monitoring (Priority: P5)

**Goal**: Verify all features work in production and document deployment

**Independent Test**: Run comprehensive verification checklist, test all features, verify health checks

### Implementation for User Story 5

- [ ] T088 [US5] Create scripts/deployment/verify-deployment.sh: Automated verification script
- [ ] T089 [US5] Verify health check endpoint: `curl https://ai-native-book-backend.onrender.com/api/health` (expect 200 OK)
- [ ] T090 [US5] Verify frontend loads: `curl -I https://ai-native-book.vercel.app` (expect 200 OK, <3s)
- [ ] T091 [US5] Verify CORS works: Check browser console for CORS errors (expect none)
- [ ] T092 [US5] Verify authentication: Signup → Login → Logout (expect all work)
- [ ] T093 [US5] Verify chatbot: Create conversation → Send message → Verify streaming response
- [ ] T094 [US5] Verify translation: Request translation → Verify Urdu text displays → Verify caching works
- [ ] T095 [US5] Verify preferences: Change language → Verify persists across sessions
- [ ] T096 [US5] Verify database connection: Check Render logs for successful Neon connections
- [ ] T097 [US5] Verify environment variables: Check Render logs for successful variable loading
- [ ] T098 [US5] Test cold start behavior: Wait 15 minutes, make request, verify 30-second wake-up - handles edge case: Render spin-down during active session
- [ ] T099 [US5] Verify error logging: Trigger error, check Render logs for error capture - handles edge case: invalid OpenAI/Qdrant credentials
- [ ] T100 [US5] Document production URLs in history.md (frontend, backend, database)
- [ ] T101 [US5] Document deployment completion date and status in history.md
- [ ] T102 [US5] Create deployment summary: Record migration results, deployment times, any issues
- [ ] T103 [US5] Verify rollback procedures documented: Database, backend, frontend rollback steps
- [ ] T104 [US5] Schedule 24-hour monitoring: Monitor health checks and error logs
- [ ] T104a [US5] (Optional) Perform load testing: Test with 100 concurrent users to verify SC-011 (can be done post-deployment)

**Checkpoint**: Production deployment complete and verified

---

## Phase 8: Polish & Documentation

**Purpose**: Final documentation and cleanup

- [ ] T105 Update history.md: Add Phase 5 deployment completion entry with production URLs
- [ ] T106 [P] Create deployment guide: Document step-by-step deployment procedure for future reference
- [ ] T107 [P] Document troubleshooting: Common issues and solutions in specs/006-production-deployment/troubleshooting.md
- [ ] T108 Tag release: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] T109 Archive SQLite backup: Move backup to safe location, retain for 7 days

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
- US1: Tasks T027-T028 (export/import) can be prepared in parallel
- US2: Tasks T041-T043 (environment variables) can be configured in parallel
- US3: Tasks T066-T071 (feature testing) can be tested in parallel
- US5: Tasks T092-T095 (feature verification) can be verified in parallel

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
# Can run in parallel after T040:
- T041: Configure OPENAI_API_KEY
- T042: Configure QDRANT_URL
- T043: Configure QDRANT_API_KEY
```

### Phase 7 (US5: Verification)
```bash
# Can run in parallel after T091:
- T092: Test authentication
- T093: Test chatbot
- T094: Test translation
- T095: Test preferences
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

**Total Tasks**: 114 (109 original + 5 added during analysis remediation)
- Phase 1 (Setup): 9 tasks (T001-T009)
- Phase 2 (Foundational): 10 tasks (T010-T019)
- Phase 3 (US1 - Database Migration): 16 tasks (T020-T035)
- Phase 4 (US2 - Backend Deployment): 18 tasks (T036-T053)
- Phase 5 (US3 - Frontend Deployment): 21 tasks (T054-T073, +T058a)
- Phase 6 (US4 - CI/CD Pipeline): 17 tasks (T074-T087, +T074a, T075a, T086a)
- Phase 7 (US5 - Verification): 18 tasks (T088-T104, +T104a)
- Phase 8 (Polish): 5 tasks (T105-T109)
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
