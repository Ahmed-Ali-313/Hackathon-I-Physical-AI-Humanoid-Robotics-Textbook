# Feature Specification: Migrate RAG Chatbot to OpenAI-Only API

**Feature Branch**: `004-openai-only`
**Created**: 2026-02-23
**Status**: Draft
**Input**: User description: "i want to update soem thing that i want to use only the open ai api in the rag chatbbot so delet the configuration of gemini api kry from the project first update the specs and then update the task plan etc amd ap.adr and then apply updation on rag chatbot and embiddings"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simplified API Configuration (Priority: P1)

As a developer setting up the RAG chatbot, I want to configure only OpenAI API credentials so that I have a simpler, more maintainable setup without managing multiple API providers.

**Why this priority**: This is the core requirement - removing dual API configuration complexity and standardizing on a single provider. This directly impacts developer experience and reduces configuration errors.

**Independent Test**: Can be fully tested by configuring only OPENAI_API_KEY environment variable, starting the backend, and verifying the chatbot responds to queries successfully without any Gemini credentials.

**Acceptance Scenarios**:

1. **Given** a fresh backend setup, **When** I configure only OPENAI_API_KEY (no GEMINI_API_KEY), **Then** the backend starts successfully without errors
2. **Given** the backend is running with OpenAI configuration, **When** I send a chat query, **Then** the chatbot responds using OpenAI API
3. **Given** the backend is running, **When** I check environment variables, **Then** no GEMINI_API_KEY or LLM_PROVIDER variables are required

---

### User Story 2 - Clean Codebase (Priority: P2)

As a developer maintaining the codebase, I want all Gemini-specific code removed so that the codebase is cleaner, easier to understand, and has no unused dependencies.

**Why this priority**: Code cleanliness and maintainability are important but secondary to functional requirements. This reduces technical debt and makes future development easier.

**Independent Test**: Can be tested by searching the codebase for Gemini-related imports, configuration, and code references, verifying none exist.

**Acceptance Scenarios**:

1. **Given** the updated codebase, **When** I search for "gemini" or "google.generativeai" imports, **Then** no results are found
2. **Given** the updated codebase, **When** I review configuration files, **Then** no Gemini API key references exist
3. **Given** the updated codebase, **When** I check dependencies, **Then** google-generativeai package is not listed

---

### User Story 3 - Updated Documentation (Priority: P3)

As a new developer joining the project, I want documentation that reflects OpenAI-only setup so that I can quickly understand the system without confusion about multiple API providers.

**Why this priority**: Documentation updates are important but can be done after functional changes. They support onboarding but don't affect system functionality.

**Independent Test**: Can be tested by reviewing all documentation files (README, constitution.md, setup guides) and verifying they only mention OpenAI API.

**Acceptance Scenarios**:

1. **Given** the updated documentation, **When** I read setup instructions, **Then** only OpenAI API key configuration is mentioned
2. **Given** the updated constitution.md, **When** I review tech stack requirements, **Then** only OpenAI is listed as the LLM provider
3. **Given** the updated documentation, **When** I search for "Gemini" or "dual API", **Then** no references are found

---

### Edge Cases

- What happens when OpenAI API is unavailable or rate-limited? (System should return appropriate error messages since there's no fallback provider)
- What happens to existing vector embeddings created with Gemini? (May need re-indexing if embedding dimensions or models differ)
- What happens if someone tries to use old environment variables (GEMINI_API_KEY, LLM_PROVIDER)? (System should ignore them or warn they're deprecated)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use only OpenAI API for chat completion and response generation
- **FR-002**: System MUST use only OpenAI API for generating text embeddings
- **FR-003**: System MUST NOT require GEMINI_API_KEY environment variable
- **FR-004**: System MUST NOT require LLM_PROVIDER environment variable (OpenAI is implicit)
- **FR-005**: System MUST remove all Gemini-specific imports and dependencies from the codebase
- **FR-006**: System MUST remove all Gemini-specific configuration code from embedding service
- **FR-007**: System MUST remove all Gemini-specific configuration code from agent service
- **FR-008**: System MUST update all documentation to reflect OpenAI-only setup
- **FR-009**: System MUST maintain all existing chatbot functionality (RAG grounding, source attribution, selection mode)
- **FR-010**: System MUST use OpenAI text-embedding-3-small model for embeddings (768 dimensions)
- **FR-011**: System MUST use OpenAI gpt-4o-mini or gpt-4o for chat completion

### Key Entities

- **Embedding Service**: Service responsible for generating text embeddings, currently supports dual providers (Gemini/OpenAI), will be simplified to OpenAI-only
- **Agent Service**: Service responsible for chat completion and response generation, currently supports dual providers, will be simplified to OpenAI-only
- **Configuration**: Environment variables and settings that control API provider selection, will be simplified to remove provider switching logic
- **Vector Embeddings**: 768-dimensional vectors stored in Qdrant, may need re-indexing if previously created with Gemini embeddings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chatbot responds to all user queries using OpenAI API without requiring Gemini credentials
- **SC-002**: Backend starts successfully with only OPENAI_API_KEY configured (no GEMINI_API_KEY or LLM_PROVIDER needed)
- **SC-003**: Codebase contains zero references to Gemini API, google.generativeai imports, or Gemini-specific configuration
- **SC-004**: All existing unit tests pass with OpenAI-only configuration
- **SC-005**: All existing integration tests pass with OpenAI-only configuration
- **SC-006**: Documentation accurately reflects OpenAI-only setup with no mentions of dual API configuration
- **SC-007**: Environment variable requirements are reduced from 3 variables (OPENAI_API_KEY, GEMINI_API_KEY, LLM_PROVIDER) to 1 variable (OPENAI_API_KEY)

## Assumptions

- OpenAI API will be the sole LLM provider going forward (no future need for provider switching)
- Existing vector embeddings in Qdrant may need re-indexing if they were created with Gemini embeddings (different model/dimensions)
- OpenAI API rate limits and costs are acceptable for the project's usage patterns
- No existing production data depends on Gemini-specific features or behavior
