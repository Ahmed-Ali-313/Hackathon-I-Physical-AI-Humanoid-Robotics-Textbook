# Implementation Plan: User Personalization System

**Branch**: `002-personalization` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-personalization/spec.md`

## Summary

Implement a user personalization system that collects hardware and software preferences once during signup, stores them in a database, and uses them to highlight relevant content sections throughout the textbook. Users see both personalized recommendations and full content, with a toggle to switch between highlighted and neutral views.

## Technical Context

**Language/Version**: TypeScript 5.x (Docusaurus frontend), Python 3.11+ (FastAPI backend)
**Primary Dependencies**:
- Frontend: Docusaurus 3.x, React 18+
- Backend: FastAPI, Better-Auth, Neon Postgres
- Database: Neon Serverless Postgres

**Storage**: Neon Postgres (user accounts, personalization profiles, preference history, content metadata)
**Testing**: Jest + React Testing Library (frontend), pytest (backend), Playwright (E2E)
**Target Platform**: Web application (desktop + mobile responsive)
**Project Type**: Web (frontend + backend)
**Performance Goals**:
- Preference retrieval: <200ms (p95)
- Preference updates: <2s persistence
- Page load with personalization: <1.5s
- Toggle view switch: <1s

**Constraints**:
- Must support 1000 concurrent users
- 99.9% uptime for preference operations
- Zero data loss for user preferences
- Preferences cached in session to minimize DB queries

**Scale/Scope**:
- ~1000 users (initial target)
- 5 hardware preference fields + 5 software experience fields
- Content metadata tags on all textbook chapters/sections
- Audit logging for all preference changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on project guidelines from CLAUDE.md and guide.md:

### ✅ Principle I: UI-First Development
- **Status**: PASS
- **Rationale**: Plan includes UI components (signup form, preference dropdowns, toggle button, highlighted sections) before backend implementation

### ✅ Principle II: Mandatory Unit Testing
- **Status**: PASS
- **Rationale**: Testing stack defined (Jest/RTL for frontend, pytest for backend), 80% coverage target for critical paths

### ✅ Principle III: History Tracking
- **Status**: PASS
- **Rationale**: PreferenceHistory entity tracks all changes; audit logging required (FR-017)

### ✅ Principle IV: Deliverables-First
- **Status**: PASS
- **Rationale**: Maps to Deliverable #3 (Authentication & Personalization bonus feature)

### ✅ Principle V: Tech Stack Locked
- **Status**: PASS
- **Rationale**: Uses required stack (Docusaurus, FastAPI, Neon Postgres, Better-Auth)

### ✅ Principle VIII: Documentation-First Research
- **Status**: PASS (will verify in Phase 0)
- **Rationale**: Phase 0 research will consult official docs for Better-Auth, Neon Postgres, Docusaurus customization

### ✅ Principle IX: Dependency Installation
- **Status**: PASS
- **Rationale**: Quickstart.md will include dependency installation steps

**Overall Gate Status**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/002-personalization/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── preferences.yaml # Preference API contracts
│   └── content.yaml     # Content metadata API contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

textbook/                # Docusaurus frontend (Phase 1 MVP already exists)
├── src/
│   ├── components/
│   │   ├── PersonalizationForm/      # NEW: Signup preference form
│   │   ├── ContentHighlight/         # NEW: Highlighted content sections
│   │   ├── ViewToggle/               # NEW: Personalized/Full view toggle
│   │   └── PreferenceBanner/         # NEW: Prompt for non-personalized users
│   ├── pages/
│   │   ├── signup.tsx                # NEW: Extended with personalization
│   │   └── profile.tsx               # NEW: Preference management
│   ├── hooks/
│   │   ├── usePersonalization.ts     # NEW: Fetch/cache user preferences
│   │   └── useContentMetadata.ts     # NEW: Match content to preferences
│   └── services/
│       └── personalizationApi.ts     # NEW: API client for preferences
└── tests/
    ├── components/                    # NEW: Component tests
    └── e2e/                          # NEW: E2E personalization flows

backend/                 # FastAPI backend (NEW for Phase 2)
├── src/
│   ├── models/
│   │   ├── user.py                   # NEW: User model (Better-Auth integration)
│   │   ├── personalization_profile.py # NEW: Preference storage
│   │   ├── content_metadata.py       # NEW: Content tags
│   │   └── preference_history.py     # NEW: Audit log
│   ├── services/
│   │   ├── preference_service.py     # NEW: Business logic for preferences
│   │   └── matching_service.py       # NEW: Content-to-preference matching
│   ├── api/
│   │   ├── preferences.py            # NEW: Preference CRUD endpoints
│   │   └── content.py                # NEW: Content metadata endpoints
│   └── middleware/
│       └── auth.py                   # NEW: Better-Auth integration
├── tests/
│   ├── unit/                         # NEW: Service/model tests
│   ├── integration/                  # NEW: API contract tests
│   └── fixtures/                     # NEW: Test data
└── database/                         # NEW: Database migrations
    └── migrations/
        ├── 001_create_users.sql
        ├── 002_create_personalization_profiles.sql
        ├── 003_create_content_metadata.sql
        └── 004_create_preference_history.sql
```

**Structure Decision**: Web application with separate frontend (Docusaurus) and backend (FastAPI). Frontend extends existing Phase 1 textbook with personalization UI components. Backend is new for Phase 2, handling preference storage, retrieval, and matching logic. Database migrations manage schema for Neon Postgres.

## Complexity Tracking

No constitution violations requiring justification.

## Phase 0: Research & Technical Decisions

**Status**: To be executed

**Research Tasks**:
1. Better-Auth integration patterns with FastAPI
2. Neon Postgres connection pooling and session management
3. Docusaurus custom React components and context providers
4. Content metadata storage strategies (frontmatter vs database)
5. Session caching patterns for user preferences

**Output**: `research.md` with decisions, rationale, and alternatives

## Phase 1: Design Artifacts

**Status**: To be executed after Phase 0

**Deliverables**:
1. `data-model.md` - Entity schemas, relationships, validation rules
2. `contracts/` - OpenAPI specs for preference and content APIs
3. `quickstart.md` - Setup instructions, dependency installation, dev workflow

## Next Steps

1. Execute Phase 0 research (resolve technical unknowns)
2. Execute Phase 1 design (create data model and contracts)
3. Run `/sp.tasks` to generate implementation task breakdown
4. Begin implementation following UI-first principle
