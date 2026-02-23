# Implementation Plan: Migrate RAG Chatbot to OpenAI-Only API

**Branch**: `004-openai-only` | **Date**: 2026-02-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-openai-only/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Remove dual API provider configuration (Gemini/OpenAI) and standardize on OpenAI-only for the RAG chatbot. This simplifies configuration from 3 environment variables (OPENAI_API_KEY, GEMINI_API_KEY, LLM_PROVIDER) to 1 (OPENAI_API_KEY), removes unused dependencies, and maintains all existing chatbot functionality (RAG grounding, source attribution, selection mode).

**Technical Approach**: Refactor embedding_service.py and agent_service.py to remove provider switching logic, update config.py to remove Gemini-related settings, remove google-generativeai dependency, update all tests, and revise documentation to reflect OpenAI-only setup.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI SDK (openai), Qdrant Client, Pydantic
**Storage**: Qdrant Cloud (vector embeddings), Neon Postgres (chat history, sessions)
**Testing**: pytest (unit, integration, E2E tests)
**Target Platform**: Linux server (Railway/Render deployment)
**Project Type**: Web application (backend API + frontend)
**Performance Goals**: <200ms p95 latency for chat responses, support 100 concurrent users
**Constraints**: Maintain 768-dimensional embeddings, preserve RAG grounding with 0.7 confidence threshold
**Scale/Scope**: 4 backend services affected (embedding, agent, config, indexing script), ~500 lines of code changes, 20+ tests to update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ⚠️ CONSTITUTION VIOLATION DETECTED (Initial Check)

**Violation**: This migration directly conflicts with Constitution v2.0.0:
- **Principle V (Tech Stack Compliance)**: Mandates "Dual API Configuration (MANDATORY)" with Gemini as primary and OpenAI as secondary
- **Principle X (RAG Chatbot Architecture)**: Tech Stack Requirements section specifies dual provider support with switching capability

**Justification**: User explicitly requested removal of Gemini API configuration to simplify the system. The dual API requirement was added for flexibility, but in practice:
1. Only one provider is used at a time (no runtime switching)
2. Managing two API keys increases configuration complexity
3. Gemini-specific code adds maintenance burden
4. OpenAI API is sufficient for all current use cases

**Resolution Path**: This plan proceeds with the migration, but **REQUIRES** constitution amendment:
- Update Constitution v2.0.0 → v3.0.0 (MAJOR version bump)
- Remove "Dual API Configuration" requirement from Principle V
- Update Principle X Tech Stack Requirements to specify OpenAI-only
- Document this as an architectural decision in ADR

**Alternative Rejected**: Keeping dual API support was rejected because it adds unnecessary complexity without providing value in the current deployment scenario.

---

### ✅ POST-DESIGN RE-EVALUATION

**Status**: Design complete, violation remains but is justified and documented

**Design Validation**:
- ✅ All existing functionality preserved (RAG grounding, source attribution, selection mode)
- ✅ API contracts unchanged (no breaking changes for clients)
- ✅ Data models unchanged (no database migrations required)
- ✅ Error handling improved (explicit OpenAI error messages)
- ✅ Configuration simplified (3 env vars → 1 env var)
- ✅ Codebase complexity reduced (~500 lines of provider-switching logic removed)

**Constitution Amendment Required**: YES
- Must update constitution.md to v3.0.0 before merging this feature
- ADR must be created documenting the decision to remove dual API support
- This is a MAJOR version change due to tech stack modification

**Proceed to Implementation**: ✅ APPROVED
- Design is sound and achieves stated goals
- Risks are documented and mitigated
- Constitution violation is justified and will be resolved via amendment

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py                      # MODIFY: Remove GEMINI_API_KEY, LLM_PROVIDER settings
│   ├── services/
│   │   ├── embedding_service.py       # MODIFY: Remove Gemini provider logic, OpenAI-only
│   │   ├── agent_service.py           # MODIFY: Remove Gemini provider logic, OpenAI-only
│   │   ├── vector_service.py          # NO CHANGE: Qdrant operations unchanged
│   │   └── chat_service.py            # NO CHANGE: Orchestration logic unchanged
│   ├── models/                        # NO CHANGE: Data models unchanged
│   ├── api/                           # NO CHANGE: REST endpoints unchanged
│   └── tools/                         # NO CHANGE: Agent tools unchanged
├── scripts/
│   ├── index_textbook.py              # MODIFY: Remove Gemini embedding generation
│   └── create_qdrant_collection.py    # NO CHANGE: Collection setup unchanged
├── tests/
│   ├── unit/
│   │   ├── test_embedding_service.py  # MODIFY: Remove Gemini test cases
│   │   ├── test_agent_service.py      # MODIFY: Remove Gemini test cases
│   │   └── test_config.py             # MODIFY: Update config tests
│   ├── integration/
│   │   └── test_chat_flow.py          # MODIFY: Update to OpenAI-only
│   └── e2e/
│       └── test_rag_chatbot.py        # VERIFY: Should pass with OpenAI
├── requirements.txt                   # MODIFY: Remove google-generativeai
└── .env.example                       # MODIFY: Remove GEMINI_API_KEY, LLM_PROVIDER

.specify/memory/
└── constitution.md                    # MODIFY: Update to v3.0.0, remove dual API requirement

README.md                              # MODIFY: Update setup instructions
```

**Structure Decision**: Web application structure (backend + frontend). This migration affects **backend only** - no frontend changes required since the API contracts remain unchanged. The frontend continues to call the same chat endpoints, unaware of the underlying provider change.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dual API Configuration (Constitution v2.0.0, Principle V & X) | User explicitly requested single provider to reduce configuration complexity and maintenance burden | Keeping dual API support adds unnecessary code paths, requires managing 2 API keys, and provides no value since only one provider is used at runtime |
| Constitution Amendment Required | Must update constitution to v3.0.0 to reflect OpenAI-only architecture | Ignoring constitution would create inconsistency between documented principles and actual implementation |
