# Implementation Plan: RAG Chatbot Integration

**Branch**: `003-rag-chatbot` | **Date**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an authenticated RAG (Retrieval-Augmented Generation) chatbot that answers student questions using textbook content. The chatbot retrieves relevant passages from the textbook via vector search (Qdrant), generates grounded responses using LLM APIs (Gemini primary, OpenAI secondary), and displays answers with source attribution in a slide-out chat panel. Key features include strict textbook grounding (0.7 confidence threshold), selection-based context mode, conversation history with 12-month retention, and professional theme-matched UI integrated into Docusaurus.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.109+, OpenAI Agents SDK (agentic logic), Google Generative AI SDK (Gemini - primary), OpenAI SDK 1.x (secondary), Qdrant Client 1.7+, asyncpg (Neon Postgres), Pydantic 2.x
- Frontend: Docusaurus 3.x, React 19, TypeScript, CSS Modules

**Storage**:
- Neon Serverless Postgres (chat messages, conversations, user sessions, chat history)
- Qdrant Cloud Free Tier (vector embeddings: 768-dim, textbook content chunks with metadata)

**Testing**:
- Backend: pytest 8.x, pytest-asyncio, httpx (TestClient)
- Frontend: Jest 29.x, React Testing Library, Playwright (E2E)

**Target Platform**:
- Backend: Linux server (Railway/Render), Python 3.11+ runtime
- Frontend: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**Project Type**: Web application (backend API + frontend Docusaurus integration)

**Performance Goals**:
- 90% of chatbot responses delivered within 5 seconds
- Chat interface opens in <1 second (95% of users)
- Typing indicator appears within 200ms
- Chat history loads within 2 seconds
- Vector search retrieval: <500ms for top-5 chunks

**Constraints**:
- RAG confidence threshold: 0.7 minimum for textbook-grounded responses
- Conversation retention: 12 months from last message
- Concurrent users: 100 initially (scalable to 5,000)
- Message length: 500 characters max (user questions)
- Response length: 2,000 characters max (chatbot answers)
- Mobile support: Screen widths down to 320px

**Scale/Scope**:
- 5,000 users total capacity
- 250,000 total messages across all users
- 50 conversation threads per user max
- 500 messages per conversation max
- 17 textbook chapters to be indexed (from Phase 1)
- Estimated 1,000-2,000 content chunks in Qdrant

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: UI-First Development
- ✅ **PASS**: Chat UI components (slide-out panel, message bubbles, input field, conversation sidebar) will be built before backend RAG logic
- Implementation order: React components → API integration → backend endpoints

### Principle II: Mandatory Unit Testing (TDD)
- ✅ **PASS**: 80% test coverage required for critical paths
- TDD approach: Write tests first for chat API, vector search, LLM integration, conversation management
- Test categories: Unit (services, utilities), Integration (API endpoints), E2E (chat flow)

### Principle III: History Tracking
- ✅ **PASS**: Will update history.md at end of implementation session with work completed, decisions made, and next steps

### Principle IV: Deliverables-First
- ✅ **PASS**: Maps directly to Deliverable #2: "Integrated RAG Chatbot"
- Core hackathon requirement, not a bonus feature

### Principle V: Tech Stack Compliance
- ✅ **PASS**: Using mandated technologies:
  - Backend: FastAPI (Python)
  - Databases: Neon Serverless Postgres + Qdrant Cloud Free Tier
  - AI/LLM: **OpenAI Agents SDK** (chatbot logic and capabilities) with dual model support (Gemini gemini-1.5-flash primary, OpenAI gpt-4o-mini secondary)
  - Frontend: Docusaurus 3.x + React 19 + TypeScript
  - Authentication: Better-Auth (from Phase 2)
  - Deployment: Vercel (frontend), Railway/Render (backend)

### Principle VI: Documentation-First Research
- ✅ **PASS**: Must research official documentation for:
  - **OpenAI Agents SDK** - agent creation, tool registration, orchestration patterns, custom model configuration
  - Google Generative AI SDK (Gemini API) - chat completion interface, embeddings
  - OpenAI SDK - models (gpt-4o-mini), embeddings (text-embedding-3-small)
  - Qdrant Client Python SDK - vector search, collection management
  - FastAPI async patterns - background tasks, streaming responses
  - Docusaurus theming - custom React components, theme integration
- Official docs referenced in research.md

### Principle VII: Dependency Installation
- ✅ **PASS**: Will install dependencies before running/testing:
  - Backend: `pip install -r requirements.txt` (add: openai-agents-sdk, google-generativeai, openai, qdrant-client)
  - Frontend: `npm install` (add: chat UI dependencies if needed)

### Principle VIII: Smallest Viable Change
- ✅ **PASS**: Focused scope - only chatbot feature, no unrelated refactoring
- Builds on existing Phase 1 (textbook) and Phase 2 (auth) without modifying them

### Principle IX: Code Quality Standards
- ✅ **PASS**: Will follow standards:
  - No hardcoded API keys (use environment variables: GEMINI_API_KEY, OPENAI_API_KEY)
  - Type hints for Python, TypeScript for frontend
  - User-friendly error messages (per FR-023 to FR-026)
  - Proper error handling for network failures, service unavailable, expired sessions

### Principle X: RAG Chatbot Architecture
- ✅ **PASS**: Implements all 5 mandatory subsections:
  - **A. Strict RAG Grounding**: 0.7 confidence threshold, retrieve from Qdrant before generating responses
  - **B. Source Attribution**: Clickable links to chapter/section in every response (FR-011, FR-012)
  - **C. Selection-Based Context**: "Ask about selection" mode using highlighted text (FR-014, FR-015)
  - **D. Uncertainty Handling**: Explicit "I don't have information" when confidence <0.7 (FR-017)
  - **E. Tone & Pedagogy**: Professional, academic, step-by-step explanations (FR-027 to FR-030)

**Overall Status**: ✅ **ALL GATES PASS** (Phase 0 research completed, Principle VI satisfied)

---

## Phase 0: Research (COMPLETE - REVISED FOR SDK)

**Status**: ✅ Complete (Revised 2026-02-22 for OpenAI Agents SDK compliance with dual API support)
**Output**: `research.md`

### Research Areas Completed

1. **OpenAI Agents SDK Architecture with Dual API Support (Constitution-Mandated)**
   - Decision: Use OpenAI Agents SDK as core framework with configurable model provider (Gemini primary, OpenAI secondary)
   - Rationale: SDK satisfies constitution requirement while dual API provides cost optimization and flexibility
   - Models: Gemini gemini-1.5-flash (primary, cost-effective) or OpenAI gpt-4o-mini (secondary, fallback)
   - Implementation: Agent configured with model parameter based on LLM_PROVIDER environment variable
   - **Key Insight**: OpenAI Agents SDK supports any chat completion compatible model, including Gemini

2. **Vector Database Setup (Qdrant)**
   - Decision: Qdrant Cloud Free Tier with 768-dim embeddings (Gemini text-embedding-004 primary, OpenAI text-embedding-3-small secondary)
   - Rationale: 1GB storage, 100k vectors, sub-500ms latency, managed service
   - Chunking: 500-1000 tokens per chunk, 100 token overlap, paragraph boundaries
   - **Confidence Calculation**: Qdrant cosine similarity score (0.0-1.0 range), threshold 0.7

3. **RAG Architecture Pattern (SDK-Driven)**
   - Decision: Agent-orchestrated RAG with tools (not direct pipeline)
   - Flow: User question → Agent calls vector_search_tool → Agent calls retrieve_context_tool → Agent generates response
   - Rationale: SDK handles orchestration, tool calling, conversation management
   - Selection Mode: Agent detects selected_text parameter, skips vector search tool

4. **Docusaurus Integration Strategy**
   - Decision: Custom theme components (Root.tsx, ChatButton, ChatPanel)
   - Rationale: Non-invasive, theme-matched, standard React patterns
   - Text Selection: Browser Selection API with React hooks

5. **Conversation Management**
   - Decision: Postgres with 12-month retention, auto-generated titles
   - Rationale: Reliable storage, simple title generation, sidebar navigation
   - Schema: conversations, chat_messages, chat_sessions tables
   - **Title Generation Edge Cases**: If question <50 chars, use full question (no "..."). If mid-word at 50 chars, truncate to last complete word + "..."

6. **Testing Strategy**
   - Decision: TDD with 3 layers (unit, integration, E2E)
   - Rationale: Constitution compliance, fast feedback, comprehensive coverage
   - Tools: pytest, TestClient, Playwright
   - **New**: Accessibility testing (keyboard nav, screen readers, WCAG 2.1 AA)

**All technical unknowns resolved. Architecture revised for OpenAI Agents SDK compliance. Ready for Phase 1.**

---

## Phase 1: Design & Contracts (COMPLETE)

**Status**: ✅ Complete
**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`

### Data Model

**Entities Defined**:
- `Conversation`: Groups messages, auto-generated title, 12-month retention
- `ChatMessage`: User questions and AI responses with source attribution
- `SourceReference`: Embedded JSONB in ChatMessage for source links
- `ChatSession`: Tracks active sessions, 30-minute expiry

**Relationships**:
- User → Conversation (1:N, cascade delete)
- Conversation → ChatMessage (1:N, cascade delete)
- User → ChatSession (1:N, cascade delete)
- ChatSession → Conversation (N:1, optional)

**Validation Rules**:
- Max 50 conversations per user
- Max 500 messages per conversation
- Max 500 chars (user), 2000 chars (AI)
- Confidence score 0.0-1.0 for AI messages
- Source references: 0-5 per response

### API Contracts

**Endpoints Defined** (OpenAPI 3.0):
- `GET /chat/conversations` - List user's conversations
- `POST /chat/conversations` - Create new conversation
- `GET /chat/conversations/{id}` - Get conversation details
- `DELETE /chat/conversations/{id}` - Delete conversation
- `GET /chat/conversations/{id}/messages` - Get messages
- `POST /chat/conversations/{id}/messages` - Send message, get AI response
- `GET /health` - Health check

**Key Features**:
- JWT authentication (Better-Auth)
- RAG grounding with 0.7 confidence threshold
- Selection-based context mode
- User-friendly error messages
- Source attribution in all responses

### Quickstart Guide

**Setup Instructions**:
- Environment setup (Python 3.11+, Node.js 20.x)
- Database migrations (Neon Postgres)
- Qdrant collection creation and textbook indexing
- Environment variables configuration
- Development server startup

**Testing Instructions**:
- Manual browser testing
- API testing with curl
- Automated testing (unit, integration, E2E)
- TDD workflow

**Deployment Instructions**:
- Backend: Railway/Render
- Frontend: Vercel
- Production environment variables

### Agent Context Update

✅ Updated `CLAUDE.md` with:
- Language: Python 3.11+ (backend), TypeScript 5.x (frontend)
- Project Type: Web application (backend API + frontend Docusaurus integration)

**Phase 1 complete. Ready for Phase 2 (task breakdown via `/sp.tasks`).**

---

## Constitution Check (Post-Design)

*Re-evaluation after Phase 1 design completion*

### Principle VI: Documentation-First Research
- ✅ **PASS**: All official documentation researched and referenced in research.md:
  - Google Generative AI SDK (Gemini API)
  - Qdrant Client Python SDK
  - OpenAI SDK (secondary API)
  - FastAPI async patterns
  - Docusaurus theming

**All constitution gates remain PASS. Design is compliant and ready for implementation.**

## Project Structure

### Documentation (this feature)

```text
specs/003-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints
│   └── README.md        # API documentation
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── chat_message.py      # ChatMessage entity
│   │   ├── conversation.py      # Conversation entity
│   │   ├── chat_session.py      # ChatSession entity
│   │   └── source_reference.py  # SourceReference entity
│   ├── services/
│   │   ├── chat_service.py      # Conversation management, message persistence
│   │   ├── agent_service.py     # OpenAI Agents SDK orchestration (CORE)
│   │   ├── vector_service.py    # Qdrant vector search operations
│   │   └── embedding_service.py # OpenAI text-embedding-3-small
│   ├── tools/
│   │   ├── vector_search_tool.py    # Agent tool: search Qdrant for relevant chunks
│   │   ├── retrieve_context_tool.py # Agent tool: retrieve and format context
│   │   └── tool_registry.py         # Register tools with agent
│   ├── api/
│   │   ├── chat.py              # Chat endpoints (send message, get history, etc.)
│   │   └── health.py            # Health check endpoint
│   ├── config.py                # Environment variables, API keys
│   └── main.py                  # FastAPI app initialization
├── tests/
│   ├── unit/
│   │   ├── test_chat_service.py
│   │   ├── test_agent_service.py
│   │   ├── test_vector_service.py
│   │   ├── test_vector_search_tool.py
│   │   └── test_embedding_service.py
│   ├── integration/
│   │   └── test_chat_api.py
│   └── conftest.py              # Test fixtures
├── scripts/
│   └── index_textbook.py        # Script to index textbook chapters into Qdrant
└── requirements.txt             # Python dependencies (openai, openai-agents-sdk, qdrant-client, asyncpg)

frontend/ (textbook/)
├── src/
│   ├── components/
│   │   ├── ChatPanel/           # Slide-out chat panel component
│   │   │   ├── index.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── ConversationSidebar.tsx
│   │   │   ├── TypingIndicator.tsx
│   │   │   └── styles.module.css
│   │   ├── ChatButton/          # Floating "Ask" button
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   └── SourceLink/          # Clickable source attribution links
│   │       ├── index.tsx
│   │       └── styles.module.css
│   ├── services/
│   │   └── chatApi.ts           # API client for chat endpoints
│   ├── hooks/
│   │   ├── useChat.ts           # Chat state management hook
│   │   └── useTextSelection.ts  # Detect text selection for "Ask about selection"
│   └── theme/
│       └── Root.tsx             # Add ChatPanel to Docusaurus root (already has AuthProvider)
└── tests/
    ├── components/
    │   ├── ChatPanel.test.tsx
    │   └── ChatButton.test.tsx
    └── e2e/
        └── chat-flow.spec.ts    # Playwright E2E tests
```

**Structure Decision**: Web application architecture with separate backend (FastAPI) and frontend (Docusaurus). Backend uses **OpenAI Agents SDK** for agentic orchestration, with RAG logic implemented as agent tools. Agent handles conversation flow, tool calling (vector search, context retrieval), and response generation. Frontend integrates chat UI as Docusaurus theme components. This structure aligns with existing Phase 1 (textbook in `textbook/`) and Phase 2 (backend in `backend/`) architecture while satisfying constitution mandate for SDK-based implementation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All constitution principles are satisfied by the proposed architecture.
