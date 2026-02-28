# Tasks: Urdu Translation for Textbook Chapters

**Input**: Design documents from `/specs/005-urdu-translation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Following TDD approach (Constitution Principle III) - tests written FIRST, must FAIL before implementation

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `textbook/src/`, `textbook/tests/`
- **Database**: `backend/migrations/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install backend dependencies: openai SDK, hashlib (built-in) in backend/requirements.txt
- [ ] T002 [P] Install frontend fonts: Add Noto Nastaliq Urdu and Noto Sans Arabic to textbook/src/theme/fonts.css
- [ ] T003 [P] Verify Python 3.12+ and Node.js 18+ installed
- [ ] T004 [P] Configure environment variables in backend/.env (OPENAI_API_KEY, DATABASE_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create database migration 006_add_translation_tables.sql in backend/migrations/
- [ ] T006 [P] Create database migration 007_add_user_language_preference.sql in backend/migrations/
- [ ] T007 Run database migrations to create translated_chapters table and extend users table
- [ ] T008 [P] Create TranslatedChapter model in backend/src/models/translated_chapter.py
- [ ] T009 [P] Extend User model with preferred_language field in backend/src/models/user.py
- [ ] T010 [P] Create translation prompt templates in backend/src/prompts/translation_prompt.py
- [ ] T011 [P] Create base validation utilities in backend/src/utils/validation.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Translate Chapter to Urdu (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can translate any chapter to Urdu with technical terms preserved, code blocks unchanged, and RTL layout applied

**Independent Test**: Login, navigate to Chapter 1, click "Translate to Urdu", verify Urdu content displays with RTL layout, technical terms in English, code blocks unchanged

### Tests for User Story 1 (TDD - Write FIRST, must FAIL)

- [ ] T012 [P] [US1] Unit test for TranslationService.translate() in backend/tests/unit/test_translation_service.py
- [ ] T013 [P] [US1] Unit test for technical term preservation in backend/tests/unit/test_translation_service.py
- [ ] T014 [P] [US1] Unit test for code block immunity in backend/tests/unit/test_translation_service.py
- [ ] T015 [P] [US1] Unit test for LaTeX preservation in backend/tests/unit/test_translation_service.py
- [ ] T016 [P] [US1] Unit test for markdown structure preservation in backend/tests/unit/test_translation_service.py
- [ ] T017 [P] [US1] Unit test for ValidationService.validate_translation() in backend/tests/unit/test_validation_service.py
- [ ] T018 [P] [US1] Integration test for POST /api/v1/translate endpoint in backend/tests/integration/test_translation_api.py
- [ ] T019 [P] [US1] E2E test for full translation flow in textbook/tests/e2e/translation.spec.ts
- [ ] T020 [P] [US1] E2E test for RTL layout in textbook/tests/e2e/rtl-layout.spec.ts

### Implementation for User Story 1

**Backend Services:**

- [ ] T021 [P] [US1] Implement TranslationService.translate() in backend/src/services/translation_service.py
- [ ] T022 [P] [US1] Implement ValidationService.validate_translation() in backend/src/services/validation_service.py
- [ ] T023 [US1] Implement ChunkingService.chunk_by_headers() in backend/src/services/chunking_service.py (depends on T021)
- [ ] T024 [US1] Add OpenAI API integration with structured prompts in backend/src/services/translation_service.py (depends on T021)
- [ ] T025 [US1] Add validation retry logic with stricter prompts in backend/src/services/translation_service.py (depends on T022)

**Backend API:**

- [ ] T026 [US1] Implement POST /api/v1/translate endpoint in backend/src/api/translation.py (depends on T021, T022)
- [ ] T027 [US1] Add authentication check (JWT validation) in backend/src/api/translation.py (depends on T026)
- [ ] T028 [US1] Add rate limiting (10 req/min) in backend/src/api/translation.py (depends on T026)
- [ ] T029 [US1] Add error handling and user-friendly messages in backend/src/api/translation.py (depends on T026)

**Frontend Components:**

- [ ] T030 [P] [US1] Create TranslationControl component in textbook/src/components/TranslationControl/index.tsx
- [ ] T031 [P] [US1] Create RTL layout styles in textbook/src/components/TranslationControl/styles.module.css
- [ ] T032 [P] [US1] Create useTranslation hook in textbook/src/hooks/useTranslation.ts
- [ ] T033 [P] [US1] Create translationApi service in textbook/src/services/translationApi.ts
- [ ] T034 [US1] Integrate TranslationControl into DocItem layout in textbook/src/theme/DocItem/index.tsx (depends on T030)
- [ ] T035 [US1] Add loading indicator during translation in textbook/src/components/TranslationControl/index.tsx (depends on T030)
- [ ] T036 [US1] Add button state toggle ("Translate to Urdu" / "Show Original English") in textbook/src/components/TranslationControl/index.tsx (depends on T030)

**Frontend Tests:**

- [ ] T037 [P] [US1] Unit test for TranslationControl component in textbook/src/components/TranslationControl/TranslationControl.test.tsx
- [ ] T038 [P] [US1] Unit test for useTranslation hook in textbook/src/hooks/useTranslation.test.ts

**Checkpoint**: At this point, User Story 1 should be fully functional - users can translate chapters to Urdu with all preservation rules working

---

## Phase 4: User Story 4 - Unauthenticated User Experience (Priority: P1)

**Goal**: Unauthenticated visitors see English only, no translate button, redirect to login if attempting to access translation

**Independent Test**: Visit textbook without logging in, verify no translate button, attempt to access translated URL, verify redirect to login

### Tests for User Story 4 (TDD - Write FIRST, must FAIL)

- [ ] T039 [P] [US4] Integration test for unauthenticated access to POST /api/v1/translate in backend/tests/integration/test_translation_api.py
- [ ] T040 [P] [US4] E2E test for unauthenticated user experience in textbook/tests/e2e/translation-auth.spec.ts

### Implementation for User Story 4

- [ ] T041 [US4] Add authentication check in TranslationControl component (hide button if not logged in) in textbook/src/components/TranslationControl/index.tsx
- [ ] T042 [US4] Add redirect to login on unauthenticated translation attempt in textbook/src/components/TranslationControl/index.tsx (depends on T041)
- [ ] T043 [US4] Add "Sign up to access Urdu translations" message in textbook/src/components/TranslationControl/index.tsx (depends on T041)

**Checkpoint**: Unauthenticated users cannot access translation feature, see clear messaging

---

## Phase 5: User Story 2 - Language Preference Persistence (Priority: P2)

**Goal**: User's language preference persists across all chapters and browser sessions

**Independent Test**: Login, translate Chapter 1 to Urdu, navigate to Chapter 2, verify auto-displays in Urdu, close browser, reopen, verify still Urdu

### Tests for User Story 2 (TDD - Write FIRST, must FAIL)

- [ ] T044 [P] [US2] Integration test for PUT /api/v1/user/preferences endpoint in backend/tests/integration/test_preferences_api.py
- [ ] T045 [P] [US2] Integration test for GET /api/v1/user/preferences endpoint in backend/tests/integration/test_preferences_api.py
- [ ] T046 [P] [US2] E2E test for preference persistence across chapters in textbook/tests/e2e/preference-persistence.spec.ts
- [ ] T047 [P] [US2] E2E test for preference persistence across sessions in textbook/tests/e2e/preference-persistence.spec.ts

### Implementation for User Story 2

**Backend API:**

- [ ] T048 [P] [US2] Implement PUT /api/v1/user/preferences endpoint in backend/src/api/preferences.py
- [ ] T049 [P] [US2] Implement GET /api/v1/user/preferences endpoint in backend/src/api/preferences.py
- [ ] T050 [US2] Add validation for preferred_language field ("en" or "ur") in backend/src/api/preferences.py (depends on T048)

**Frontend State Management:**

- [ ] T051 [US2] Create LanguageContext for global language state in textbook/src/contexts/LanguageContext.tsx
- [ ] T052 [US2] Update useTranslation hook to use LanguageContext in textbook/src/hooks/useTranslation.ts (depends on T051)
- [ ] T053 [US2] Add preference save on language toggle in textbook/src/hooks/useTranslation.ts (depends on T051)
- [ ] T054 [US2] Add preference load on app initialization in textbook/src/theme/Root.tsx (depends on T051)
- [ ] T055 [US2] Apply saved preference to all chapters automatically in textbook/src/theme/DocItem/index.tsx (depends on T051)

**Checkpoint**: Language preference persists across chapters and sessions

---

## Phase 6: User Story 3 - Fast Translation with Caching (Priority: P3)

**Goal**: Translated chapters load instantly (<500ms) on subsequent visits through database caching

**Independent Test**: Translate Chapter 1 (may take 3-5s), navigate away, return to Chapter 1, verify loads instantly (<500ms)

### Tests for User Story 3 (TDD - Write FIRST, must FAIL)

- [ ] T056 [P] [US3] Unit test for CacheService.get_cached_translation() in backend/tests/unit/test_cache_service.py
- [ ] T057 [P] [US3] Unit test for CacheService.save_translation() in backend/tests/unit/test_cache_service.py
- [ ] T058 [P] [US3] Unit test for optimistic locking (version field) in backend/tests/unit/test_cache_service.py
- [ ] T059 [P] [US3] Unit test for cache invalidation (hash mismatch) in backend/tests/unit/test_cache_service.py
- [ ] T060 [P] [US3] Unit test for cache expiration (30 days) in backend/tests/unit/test_cache_service.py
- [ ] T061 [P] [US3] Integration test for GET /api/v1/translate/{chapter_id} endpoint in backend/tests/integration/test_translation_api.py
- [ ] T062 [P] [US3] Integration test for concurrent translation requests in backend/tests/integration/test_cache_integration.py
- [ ] T063 [P] [US3] E2E test for cache hit performance (<500ms) in textbook/tests/e2e/translation-performance.spec.ts

### Implementation for User Story 3

**Backend Caching:**

- [ ] T064 [P] [US3] Implement CacheService.get_cached_translation() in backend/src/services/cache_service.py
- [ ] T065 [P] [US3] Implement CacheService.save_translation() in backend/src/services/cache_service.py
- [ ] T066 [US3] Implement optimistic locking with version field in backend/src/services/cache_service.py (depends on T064, T065)
- [ ] T067 [US3] Implement content hash computation (SHA-256) in backend/src/services/cache_service.py (depends on T064)
- [ ] T068 [US3] Implement cache invalidation on hash mismatch in backend/src/services/cache_service.py (depends on T067)
- [ ] T069 [US3] Implement cache expiration (30 days) in backend/src/services/cache_service.py (depends on T064)
- [ ] T070 [US3] Integrate cache-first strategy in TranslationService in backend/src/services/translation_service.py (depends on T064, T065)

**Backend API:**

- [ ] T071 [US3] Implement GET /api/v1/translate/{chapter_id} endpoint in backend/src/api/translation.py (depends on T064)
- [ ] T072 [US3] Update POST /api/v1/translate to check cache first in backend/src/api/translation.py (depends on T070)

**Frontend Optimization:**

- [ ] T073 [US3] Add cache status indicator ("cached" vs "fresh") in textbook/src/components/TranslationControl/index.tsx
- [ ] T074 [US3] Optimize loading states for cached vs fresh translations in textbook/src/components/TranslationControl/index.tsx (depends on T073)

**Checkpoint**: Cached translations load instantly, 80%+ cache hit rate after first week

---

## Phase 7: User Story 5 - Background-Aware Translation (Priority: P4) [OPTIONAL]

**Goal**: Translation complexity adjusts based on user's technical background level (beginner/intermediate/advanced)

**Independent Test**: Create two accounts with different background levels, translate same chapter, verify different complexity levels

### Tests for User Story 5 (TDD - Write FIRST, must FAIL)

- [ ] T075 [P] [US5] Unit test for beginner-level translation prompt in backend/tests/unit/test_translation_service.py
- [ ] T076 [P] [US5] Unit test for advanced-level translation prompt in backend/tests/unit/test_translation_service.py
- [ ] T077 [P] [US5] E2E test for background-aware translation in textbook/tests/e2e/translation-background.spec.ts

### Implementation for User Story 5

- [ ] T078 [US5] Add user_level parameter to TranslationService.translate() in backend/src/services/translation_service.py
- [ ] T079 [US5] Implement beginner-level prompt template in backend/src/prompts/translation_prompt.py (depends on T078)
- [ ] T080 [US5] Implement advanced-level prompt template in backend/src/prompts/translation_prompt.py (depends on T078)
- [ ] T081 [US5] Pass user background level from API to service in backend/src/api/translation.py (depends on T078)

**Checkpoint**: Translation complexity adapts to user's technical background

---

## Phase 8: Admin Features

**Goal**: Administrators can manually invalidate cached translations

**Independent Test**: Login as admin, invalidate Chapter 1 cache, verify next translation request is fresh

### Tests for Admin Features (TDD - Write FIRST, must FAIL)

- [ ] T082 [P] Integration test for DELETE /api/v1/admin/cache/{chapter_id} endpoint in backend/tests/integration/test_admin_api.py
- [ ] T083 [P] Integration test for admin role check in backend/tests/integration/test_admin_api.py

### Implementation for Admin Features

- [ ] T084 [P] Implement DELETE /api/v1/admin/cache/{chapter_id} endpoint in backend/src/api/admin.py
- [ ] T085 [US3] Add admin role check (JWT validation) in backend/src/api/admin.py (depends on T084)
- [ ] T086 [US3] Implement cache deletion logic in backend/src/services/cache_service.py (depends on T084)
- [ ] T087 [US3] Add bulk cache invalidation (all chapters) in backend/src/api/admin.py (depends on T084)

**Checkpoint**: Admins can manually invalidate cache for re-translation

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T088 [P] Add comprehensive logging for all translation operations in backend/src/services/translation_service.py
- [ ] T089 [P] Add performance metrics tracking (translation latency, cache hit rate) in backend/src/services/metrics_service.py
- [ ] T090 [P] Add error monitoring and alerting in backend/src/services/translation_service.py
- [ ] T091 [P] Optimize font loading (preload Noto Nastaliq Urdu) in textbook/src/theme/fonts.css
- [ ] T092 [P] Add accessibility tests (keyboard navigation, screen reader) in textbook/tests/e2e/accessibility.spec.ts
- [ ] T093 [P] Add visual regression tests for RTL layout in textbook/tests/e2e/visual-regression.spec.ts
- [ ] T094 [P] Create deployment guide in specs/005-urdu-translation/DEPLOYMENT.md
- [ ] T095 [P] Update README with translation feature documentation in README.md
- [ ] T096 Run full test suite (backend: pytest, frontend: npm test)
- [ ] T097 Run E2E tests (npm run test:e2e)
- [ ] T098 Validate quickstart.md instructions (manual walkthrough)
- [ ] T099 Performance testing: Load test translation endpoint (10 concurrent users, 100 requests)
- [ ] T100 Performance testing: Verify cache hit rate >80% after 1 week simulation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US4 (P1): Can start after Foundational - Depends on US1 (needs TranslationControl component)
  - US2 (P2): Can start after Foundational - Depends on US1 (needs translation functionality)
  - US3 (P3): Can start after Foundational - Depends on US1 (needs translation service)
  - US5 (P4): Can start after Foundational - Depends on US1 (extends translation service)
- **Admin (Phase 8)**: Depends on US3 (needs cache service)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories ✅ MVP
- **User Story 4 (P1)**: Depends on US1 (needs TranslationControl component)
- **User Story 2 (P2)**: Depends on US1 (needs translation functionality)
- **User Story 3 (P3)**: Depends on US1 (needs translation service)
- **User Story 5 (P4)**: Depends on US1 (extends translation service) - OPTIONAL

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T004)
- All Foundational tasks marked [P] can run in parallel (T008-T011)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- After Foundational phase, US1 can start immediately (MVP path)
- After US1 completes, US2, US3, US4, US5 can work in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task T012: "Unit test for TranslationService.translate()"
Task T013: "Unit test for technical term preservation"
Task T014: "Unit test for code block immunity"
Task T015: "Unit test for LaTeX preservation"
Task T016: "Unit test for markdown structure preservation"
Task T017: "Unit test for ValidationService.validate_translation()"
Task T018: "Integration test for POST /api/v1/translate endpoint"
Task T019: "E2E test for full translation flow"
Task T020: "E2E test for RTL layout"

# After tests written and failing, launch all backend services together:
Task T021: "Implement TranslationService.translate()"
Task T022: "Implement ValidationService.validate_translation()"

# Launch all frontend components together:
Task T030: "Create TranslationControl component"
Task T031: "Create RTL layout styles"
Task T032: "Create useTranslation hook"
Task T033: "Create translationApi service"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 4 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T038) - Core translation
4. Complete Phase 4: User Story 4 (T039-T043) - Auth enforcement
5. **STOP and VALIDATE**: Test US1 + US4 independently
6. Deploy/demo if ready - **This is the MVP!**

**MVP Scope**: 43 tasks (Setup + Foundational + US1 + US4)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (11 tasks)
2. Add User Story 1 + User Story 4 → Test independently → Deploy/Demo (MVP! 43 tasks total)
3. Add User Story 2 → Test independently → Deploy/Demo (55 tasks total)
4. Add User Story 3 → Test independently → Deploy/Demo (74 tasks total)
5. Add User Story 5 (optional) → Test independently → Deploy/Demo (81 tasks total)
6. Add Admin Features → Test independently → Deploy/Demo (87 tasks total)
7. Add Polish → Final production release (100 tasks total)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (11 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (27 tasks)
   - Developer B: User Story 4 (5 tasks) - quick win
3. After US1 completes:
   - Developer A: User Story 2 (12 tasks)
   - Developer B: User Story 3 (19 tasks)
   - Developer C: User Story 5 (7 tasks, optional)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 100

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1 - Translate Chapter): 27 tasks
- Phase 4 (US4 - Auth Enforcement): 5 tasks
- Phase 5 (US2 - Preference Persistence): 12 tasks
- Phase 6 (US3 - Caching): 19 tasks
- Phase 7 (US5 - Background-Aware): 7 tasks (optional)
- Phase 8 (Admin Features): 4 tasks
- Phase 9 (Polish): 13 tasks

**By User Story**:
- US1 (P1): 27 tasks - Core translation functionality
- US4 (P1): 5 tasks - Authentication enforcement
- US2 (P2): 12 tasks - Preference persistence
- US3 (P3): 19 tasks - Caching and performance
- US5 (P4): 7 tasks - Background-aware (optional)

**MVP Scope**: 43 tasks (Setup + Foundational + US1 + US4)

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD approach: Write tests FIRST, verify they FAIL, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = US1 + US4 (43 tasks) - delivers core value
- US2, US3, US5 are enhancements that can be added incrementally
