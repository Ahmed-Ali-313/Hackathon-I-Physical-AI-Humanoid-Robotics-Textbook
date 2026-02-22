---
id: 0002
title: Create ADR for SDK architecture
stage: plan
date: 2026-02-22
surface: agent
model: Claude Opus 4.6 (1M context)
feature: 003-rag-chatbot
branch: 003-rag-chatbot
user: developer
command: /sp.adr
labels: ["adr", "architecture", "openai-agents-sdk", "documentation"]
links:
  spec: specs/003-rag-chatbot/spec.md
  ticket: null
  adr: history/adr/0006-openai-agents-sdk-integration-for-rag-orchestration.md
  pr: null
files:
  - history/adr/0006-openai-agents-sdk-integration-for-rag-orchestration.md
  - history/adr/0003-rag-architecture-pattern.md
tests:
  - No tests (documentation phase)
---

## Prompt

User invoked `/sp.adr` command to analyze planning artifacts and document architecturally significant decisions as Architecture Decision Records.

Context: After completing analysis and redesign session (PHR-0001), the architecture was changed from direct API pipeline to OpenAI Agents SDK with agent tools pattern. This fundamental architectural change required documentation as an ADR.

## Response snapshot

**Analysis Results:**
- Loaded planning context from specs/003-rag-chatbot/
- Reviewed existing ADRs (0001-0005)
- Identified architectural decision: OpenAI Agents SDK integration
- Found ADR-0003 (RAG Architecture Pattern) described old three-stage pipeline approach
- Created ADR-0006 to document SDK-driven architecture
- Updated ADR-0003 status to "Superseded by ADR-0006"

**ADR-0006 Created:**
- Title: OpenAI Agents SDK Integration for RAG Orchestration
- Status: Accepted
- Context: Constitution mandate for SDK, redesign from direct pipeline
- Decision: SDK as core framework with dual API support (Gemini/OpenAI), agent tools pattern (vector_search_tool, retrieve_context_tool)
- Consequences: Constitution compliance, orchestration benefits, increased complexity
- Alternatives: Direct pipeline (rejected - constitution violation), LangChain (rejected - wrong SDK), custom framework (rejected - over-engineering)

**Significance Test:**
✅ Impact: Fundamental change to chatbot architecture
✅ Alternatives: 4 alternatives considered with tradeoffs
✅ Scope: Cross-cutting concern affecting all chatbot functionality

## Outcome

- ✅ Impact: Created ADR-0006 documenting SDK architecture, updated ADR-0003 to superseded status
- 🧪 Tests: No tests (documentation phase)
- 📁 Files: 2 ADRs modified (0003, 0006)
- 🔁 Next prompts: Ready for /sp.implement to begin implementation
- 🧠 Reflection: ADR captures critical architectural decision driven by constitution compliance. SDK approach adds complexity but provides orchestration benefits and satisfies mandatory requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None - ADR creation successful
- Graders run and results (PASS/FAIL): Significance test PASS (all 3 criteria met: impact, alternatives, scope)
- Prompt variant (if applicable): Standard /sp.adr workflow
- Next experiment (smallest change to try): Begin implementation with Phase 1 (Setup) tasks
