---
id: 003
title: Create RAG Chatbot Implementation Plan
stage: plan
date: 2026-02-22
surface: agent
model: claude-opus-4-6
feature: 003-rag-chatbot
branch: 003-rag-chatbot
user: ahmeddev
command: /sp.plan
labels: ["rag-chatbot", "planning", "architecture", "gemini-api", "qdrant", "dual-api"]
links:
  spec: specs/003-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-rag-chatbot/plan.md
 - specs/003-rag-chatbot/research.md
 - specs/003-rag-chatbot/data-model.md
 - specs/003-rag-chatbot/contracts/chat-api.yaml
 - specs/003-rag-chatbot/contracts/README.md
 - specs/003-rag-chatbot/quickstart.md
 - CLAUDE.md (updated with new technologies)
tests:
 - None (planning phase)
---

## Prompt

(User invoked /sp.plan to create implementation plan for RAG chatbot feature)

## Response snapshot

Completed comprehensive implementation plan with Phase 0 (Research) and Phase 1 (Design & Contracts).

**Phase 0: Research (research.md)**

Researched and documented 6 key technical decisions:

1. **Dual API Configuration**: Gemini primary (gemini-1.5-flash), OpenAI secondary (gpt-4o-mini)
   - Rationale: Cost efficiency, generous free tier, constitution compliance
   - Implementation: Provider abstraction layer with config-based switching

2. **Vector Database**: Qdrant Cloud Free Tier with 768-dim embeddings
   - Rationale: 1GB storage, 100k vectors, sub-500ms latency, managed service
   - Chunking: 500-1000 tokens per chunk, 100 token overlap

3. **RAG Architecture**: Three-stage pipeline (Embed → Retrieve → Generate)
   - Confidence threshold: 0.7 (per constitution)
   - Selection mode: Skip retrieval, use selected text directly

4. **Docusaurus Integration**: Custom theme components (Root.tsx, ChatButton, ChatPanel)
   - Non-invasive, theme-matched, standard React patterns

5. **Conversation Management**: Postgres with 12-month retention, auto-generated titles
   - Schema: conversations, chat_messages, chat_sessions tables

6. **Testing Strategy**: TDD with 3 layers (unit, integration, E2E)
   - Tools: pytest, TestClient, Playwright

**Phase 1: Design & Contracts**

Created comprehensive design documentation:

1. **Data Model (data-model.md)**:
   - 4 entities: Conversation, ChatMessage, SourceReference (embedded), ChatSession
   - Relationships: User → Conversation (1:N), Conversation → ChatMessage (1:N)
   - Validation: Max 50 conversations/user, 500 messages/conversation
   - Storage estimate: ~5 GB for 5,000 users

2. **API Contracts (contracts/)**:
   - OpenAPI 3.0 specification (chat-api.yaml)
   - 7 endpoints: conversations CRUD, messages, health check
   - JWT authentication (Better-Auth)
   - Comprehensive error responses

3. **API Documentation (contracts/README.md)**:
   - Request/response examples
   - Error handling guide
   - Testing instructions (curl, Postman)

4. **Quickstart Guide (quickstart.md)**:
   - Environment setup (Python 3.11+, Node.js 20.x)
   - Database migrations (Neon Postgres)
   - Qdrant indexing script
   - Development workflow (TDD)
   - Deployment instructions (Railway/Render, Vercel)

**Constitution Compliance**:
- ✅ All 10 principles validated
- ✅ Principle VI satisfied: Official documentation researched (Gemini, Qdrant, OpenAI, FastAPI, Docusaurus)
- ✅ Principle X satisfied: All 5 RAG architecture subsections implemented

**Technical Context**:
- Languages: Python 3.11+ (backend), TypeScript 5.x (frontend)
- Dependencies: FastAPI, Qdrant Client, Google Generative AI SDK, OpenAI SDK, asyncpg
- Storage: Neon Postgres + Qdrant Cloud Free Tier
- Testing: pytest, Jest, Playwright
- Performance: 90% responses <5s, 95% interface opens <1s
- Scale: 5,000 users, 250,000 conversations, 5M messages

**Project Structure**:
- Backend: models/, services/, api/ (RAG logic, vector search, LLM integration)
- Frontend: components/ChatPanel/, hooks/, services/ (slide-out UI, state management)
- Tests: unit/, integration/, e2e/ (TDD approach)

**Files Created**: 6 planning artifacts + 1 agent context update

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown (/sp.tasks)
- 🧪 Tests: None (planning phase)
- 📁 Files: 7 files created/updated
- 🔁 Next prompts: /sp.adr (extract ADRs), then /sp.tasks (create task breakdown)
- 🧠 Reflection: Comprehensive planning with dual API configuration (Gemini/OpenAI), RAG architecture (0.7 threshold), and Docusaurus integration. All constitution principles satisfied. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 10 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.adr to extract architectural decisions, then /sp.tasks for implementation breakdown
