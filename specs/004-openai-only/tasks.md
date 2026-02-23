# Tasks: Migrate RAG Chatbot to OpenAI-Only API

**Input**: Design documents from `/specs/004-openai-only/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included to verify migration success and maintain existing functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`, `backend/scripts/`
- Frontend unchanged (API contracts remain the same)

---

## Phase 1: Setup (Pre-Migration Verification)

**Purpose**: Verify current state and prepare for migration

- [ ] T001 Verify current branch is 004-openai-only and up to date with 003-rag-chatbot
- [ ] T002 [P] Check Qdrant collection metadata to determine if embeddings are OpenAI or Gemini
- [ ] T003 [P] Backup current backend/.env configuration
- [ ] T004 Document current test baseline (run pytest and record pass/fail counts)

---

## Phase 2: User Story 1 - Simplified API Configuration (Priority: P1) 🎯 MVP

**Goal**: Make the RAG chatbot work with OpenAI-only configuration, removing all Gemini provider logic

**Independent Test**: Configure only OPENAI_API_KEY, start backend, send chat query, verify response uses OpenAI

### Configuration Changes

- [ ] T005 [P] [US1] Update backend/src/config.py to remove gemini_api_key and llm_provider settings
- [ ] T006 [P] [US1] Update backend/.env.example to remove GEMINI_API_KEY and LLM_PROVIDER variables

### Service Refactoring

- [ ] T007 [US1] Refactor backend/src/services/embedding_service.py to OpenAI-only (remove provider parameter, Gemini methods, use text-embedding-3-small)
- [ ] T008 [US1] Refactor backend/src/services/agent_service.py to OpenAI-only (remove provider parameter, Gemini methods, use gpt-4o-mini)
- [ ] T009 [US1] Update backend/scripts/index_textbook.py to remove Gemini embedding generation logic

### Verification

- [ ] T010 [US1] Test backend starts successfully with only OPENAI_API_KEY configured
- [ ] T011 [US1] Test chat endpoint responds using OpenAI API (verify in logs)
- [ ] T012 [US1] Verify RAG grounding still works (confidence >0.7, source attribution)
- [ ] T013 [US1] Verify selection mode still works (user highlights text, asks question)

**Checkpoint**: At this point, the chatbot should be fully functional with OpenAI-only configuration

---

## Phase 3: User Story 2 - Clean Codebase (Priority: P2)

**Goal**: Remove all Gemini-specific code, imports, and dependencies from the codebase

**Independent Test**: Search codebase for "gemini" and "google.generativeai", verify zero results

### Dependency Cleanup

- [ ] T014 [US2] Remove google-generativeai from backend/requirements.txt
- [ ] T015 [US2] Run pip install -r requirements.txt to verify no dependency conflicts

### Test Updates

- [ ] T016 [P] [US2] Update backend/tests/unit/test_embedding_service.py to remove Gemini provider test cases
- [ ] T017 [P] [US2] Update backend/tests/unit/test_agent_service.py to remove Gemini provider test cases
- [ ] T018 [P] [US2] Update backend/tests/unit/test_config.py to remove gemini_api_key and llm_provider tests
- [ ] T019 [US2] Update backend/tests/integration/test_chat_flow.py to OpenAI-only expectations
- [ ] T020 [US2] Run full test suite (pytest backend/tests/ -v) and verify all tests pass

### Code Verification

- [ ] T021 [US2] Search codebase for "gemini" references (grep -r "gemini" backend/src/) and verify none found
- [ ] T022 [US2] Search codebase for "google.generativeai" imports and verify none found
- [ ] T023 [US2] Verify backend/requirements.txt does not contain google-generativeai

**Checkpoint**: At this point, the codebase should be clean of all Gemini references and all tests passing

---

## Phase 4: User Story 3 - Updated Documentation (Priority: P3)

**Goal**: Update all documentation to reflect OpenAI-only setup with no mentions of dual API configuration

**Independent Test**: Review all documentation files and verify only OpenAI API is mentioned

### Constitution Amendment

- [ ] T024 [US3] Update .specify/memory/constitution.md to v3.0.0 (MAJOR version bump)
- [ ] T025 [US3] Remove "Dual API Configuration" requirement from Principle V in constitution.md
- [ ] T026 [US3] Update Principle X Tech Stack Requirements to specify OpenAI-only in constitution.md
- [ ] T027 [US3] Update constitution.md version footer (Version: 3.0.0, Last Amended: 2026-02-23)

### Documentation Updates

- [ ] T028 [P] [US3] Update README.md to remove Gemini API setup instructions
- [ ] T029 [P] [US3] Update README.md to reflect single environment variable (OPENAI_API_KEY only)
- [ ] T030 [P] [US3] Search all documentation for "Gemini" or "dual API" and remove references

### Verification

- [ ] T031 [US3] Verify constitution.md shows v3.0.0 and no dual API requirement
- [ ] T032 [US3] Verify README.md only mentions OpenAI API
- [ ] T033 [US3] Search documentation for "GEMINI_API_KEY" and verify none found

**Checkpoint**: All documentation should now accurately reflect OpenAI-only architecture

---

## Phase 5: Polish & Final Verification

**Purpose**: Final checks and optional re-indexing if needed

### Embedding Compatibility Check

- [ ] T034 Check Qdrant collection metadata from T002 - if Gemini embeddings detected, proceed with T035-T036
- [ ] T035 [CONDITIONAL] If Gemini embeddings: Run backend/scripts/index_textbook.py with OpenAI configuration
- [ ] T036 [CONDITIONAL] If re-indexed: Verify Qdrant collection has 768-dimensional OpenAI embeddings

### Final Validation

- [ ] T037 Run quickstart.md validation steps (10-step migration guide)
- [ ] T038 Verify all success criteria from spec.md are met (SC-001 through SC-007)
- [ ] T039 Run full test suite one final time (pytest backend/tests/ -v --cov)
- [ ] T040 Update history.md with migration session summary

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup completion - Core functional migration
- **User Story 2 (Phase 3)**: Depends on US1 completion - Cleanup after functional changes
- **User Story 3 (Phase 4)**: Can start after US1, parallel with US2 - Documentation updates
- **Polish (Phase 5)**: Depends on all user stories complete - Final verification

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (need functional system before cleanup) - Independently testable
- **User Story 3 (P3)**: Can start after US1, parallel with US2 - Independently testable

### Within Each User Story

**User Story 1 (Simplified API Configuration)**:
- Configuration changes (T005-T006) can run in parallel
- Service refactoring (T007-T009) must be sequential (T007 → T008 → T009)
- Verification (T010-T013) must be sequential after refactoring

**User Story 2 (Clean Codebase)**:
- Dependency cleanup (T014-T015) must be sequential
- Test updates (T016-T018) can run in parallel
- Integration test (T019) after unit tests
- Code verification (T021-T023) can run in parallel

**User Story 3 (Updated Documentation)**:
- Constitution amendment (T024-T027) must be sequential
- Documentation updates (T028-T030) can run in parallel
- Verification (T031-T033) can run in parallel

### Parallel Opportunities

- **Setup Phase**: T002 and T003 can run in parallel
- **US1 Configuration**: T005 and T006 can run in parallel
- **US2 Test Updates**: T016, T017, T018 can run in parallel
- **US2 Code Verification**: T021, T022, T023 can run in parallel
- **US3 Documentation**: T028, T029, T030 can run in parallel
- **US3 Verification**: T031, T032, T033 can run in parallel
- **US2 and US3**: Can work on these in parallel after US1 completes

---

## Parallel Example: User Story 1

```bash
# Configuration changes can run together:
Task T005: "Update backend/src/config.py to remove gemini_api_key and llm_provider settings"
Task T006: "Update backend/.env.example to remove GEMINI_API_KEY and LLM_PROVIDER variables"

# Service refactoring must be sequential (shared dependencies):
Task T007: "Refactor backend/src/services/embedding_service.py to OpenAI-only"
  ↓
Task T008: "Refactor backend/src/services/agent_service.py to OpenAI-only"
  ↓
Task T009: "Update backend/scripts/index_textbook.py to remove Gemini embedding generation logic"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify current state)
2. Complete Phase 2: User Story 1 (functional migration)
3. **STOP and VALIDATE**: Test chatbot with OpenAI-only
4. If working, proceed to cleanup

### Incremental Delivery

1. Complete Setup → Know current state
2. Complete US1 → Functional OpenAI-only system (MVP!)
3. Complete US2 → Clean codebase, all tests passing
4. Complete US3 → Documentation updated, constitution amended
5. Complete Polish → Final verification, ready to merge

### Parallel Team Strategy

With multiple developers:

1. Developer A: Complete Setup + US1 (critical path)
2. Once US1 done:
   - Developer A: US2 (cleanup and tests)
   - Developer B: US3 (documentation and constitution)
3. Both complete → Final polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- T034-T036 are conditional based on Qdrant embedding source
- Constitution amendment (T024-T027) is REQUIRED before merging
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Frontend unchanged - API contracts remain the same

---

## Task Summary

**Total Tasks**: 40 (37 required + 3 conditional)
- Phase 1 (Setup): 4 tasks
- Phase 2 (US1 - Simplified API Configuration): 9 tasks
- Phase 3 (US2 - Clean Codebase): 10 tasks
- Phase 4 (US3 - Updated Documentation): 10 tasks
- Phase 5 (Polish): 7 tasks (4 required + 3 conditional)

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phase 1 + Phase 2 (13 tasks) = Functional OpenAI-only chatbot

**Constitution Amendment**: REQUIRED in Phase 4 (T024-T027) before merging to main branch
