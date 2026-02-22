---
id: 004
title: Extract RAG Chatbot Architectural Decisions
stage: plan
date: 2026-02-22
surface: agent
model: claude-opus-4-6
feature: 003-rag-chatbot
branch: 003-rag-chatbot
user: ahmeddev
command: /sp.adr
labels: ["adr", "architecture", "rag-chatbot", "decision-records"]
links:
  spec: specs/003-rag-chatbot/spec.md
  ticket: null
  adr: history/adr/0002-llm-and-vector-database-stack.md
  pr: null
files:
 - history/adr/0002-llm-and-vector-database-stack.md
 - history/adr/0003-rag-architecture-pattern.md
 - history/adr/0004-frontend-chat-ui-integration.md
 - history/adr/0005-conversation-management-and-data-persistence.md
tests:
 - None (documentation phase)
---

## Prompt

(User invoked /sp.adr to extract architectural decisions from planning artifacts and create ADRs)

## Response snapshot

Extracted 4 architecturally significant decision clusters from planning artifacts and created comprehensive ADRs.

**ADRs Created:**

1. **ADR-0002: LLM and Vector Database Stack**
   - Decision: Gemini primary (gemini-1.5-flash), OpenAI secondary (gpt-4o-mini), Qdrant Cloud Free Tier
   - Rationale: Cost efficiency, flexibility, constitution compliance, managed infrastructure
   - Alternatives: OpenAI+Pinecone, Gemini+ChromaDB, Multiple LLMs+Weaviate, PostgreSQL pgvector

2. **ADR-0003: RAG Architecture Pattern**
   - Decision: Three-stage pipeline (Embed → Retrieve → Generate), 0.7 confidence threshold, selection mode
   - Rationale: Grounding, source attribution, simplicity, fast performance, constitution compliance
   - Alternatives: Multi-hop RAG, Re-ranking, Hybrid search, Agentic RAG

3. **ADR-0004: Frontend Chat UI Integration**
   - Decision: Docusaurus theme components (Root.tsx), slide-out panel, React Context, theme matching
   - Rationale: Non-invasive, theme matching, standard React patterns, no ejecting
   - Alternatives: Docusaurus plugin, separate page, iframe embed, browser extension

4. **ADR-0005: Conversation Management and Data Persistence**
   - Decision: Neon Postgres, 12-month retention, auto-generated titles, sidebar navigation
   - Rationale: Persistence, retention balance, simple title generation, queryable
   - Alternatives: AI-generated titles, timestamp-only, Redis, indefinite retention

**Decision Clustering Applied:**
- Grouped LLM + Vector DB (work together, change together)
- Grouped RAG pipeline stages (integrated approach)
- Grouped UI integration components (Docusaurus theme system)
- Grouped conversation storage + retention + navigation (data management cluster)

**Significance Test Results:**
All 4 ADRs passed significance checklist:
- ✅ Impact: Long-term architectural consequences
- ✅ Alternatives: Multiple viable options evaluated with tradeoffs
- ✅ Scope: Cross-cutting concerns affecting multiple components

**Existing ADRs Referenced:**
- ADR-0001: Documentation Platform Stack (from Phase 1, no conflicts)

**No Conflicts Detected:** All new ADRs are additive, no superseding required.

## Outcome

- ✅ Impact: 4 architectural decisions documented with rationale and alternatives
- 🧪 Tests: None (documentation phase)
- 📁 Files: 4 ADR files created
- 🔁 Next prompts: /sp.tasks (create implementation task breakdown)
- 🧠 Reflection: Successfully extracted and documented all major architectural decisions from planning phase. Decision clustering avoided over-granular ADRs. All alternatives evaluated with clear rationale for rejection. Ready for task breakdown and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Significance checklist - PASS (all 4 ADRs)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.tasks for implementation task breakdown
