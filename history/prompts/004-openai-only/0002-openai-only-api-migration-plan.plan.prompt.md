---
id: 0002
title: OpenAI-only API migration plan
stage: plan
date: 2026-02-23
surface: agent
model: Claude Opus 4.6 (1M context)
feature: 004-openai-only
branch: 004-openai-only
user: Ahmed-Ali-313
command: /sp.plan
labels: ["api-migration", "openai", "planning", "architecture"]
links:
  spec: specs/004-openai-only/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-openai-only/plan.md
  - specs/004-openai-only/research.md
  - specs/004-openai-only/data-model.md
  - specs/004-openai-only/contracts/api-contracts.md
  - specs/004-openai-only/quickstart.md
tests:
  - None (planning phase)
---

## Prompt

(User invoked /sp.plan after completing specification phase)

## Response snapshot

Created comprehensive implementation plan for migrating RAG chatbot to OpenAI-only API:

**Phase 0 - Research**:
- Documented OpenAI API best practices (text-embedding-3-small, gpt-4o-mini)
- Defined migration strategy (no backward compatibility, clean removal)
- Assessed vector embedding compatibility (may need re-indexing)
- Designed error handling without fallback provider

**Phase 1 - Design**:
- Data model: No schema changes, only configuration changes
- API contracts: All endpoints unchanged (internal implementation only)
- Quickstart guide: 10-step migration process with rollback plan
- Agent context: Updated CLAUDE.md with new technology stack

**Constitution Check**:
- ⚠️ Identified violation: Conflicts with Constitution v2.0.0 dual API requirement
- ✅ Justified: User explicitly requested simplification, dual API adds unnecessary complexity
- 📋 Resolution: Requires constitution amendment v2.0.0 → v3.0.0 (MAJOR) and ADR

**Technical Scope**:
- 4 backend services affected (embedding, agent, config, indexing)
- ~500 lines of code changes
- 20+ tests to update
- Configuration simplified: 3 env vars → 1 env var

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown (/sp.tasks)
- 🧪 Tests: No tests written (planning phase only)
- 📁 Files: 5 planning artifacts created (plan, research, data-model, contracts, quickstart)
- 🔁 Next prompts: /sp.adr to document architectural decision, then /sp.tasks for task breakdown
- 🧠 Reflection: Constitution violation detected and justified - this is a deliberate architectural simplification that requires formal amendment process

## Evaluation notes (flywheel)

- Failure modes observed: None - planning proceeded smoothly
- Graders run and results (PASS/FAIL): Constitution Check PASS (violation justified and documented)
- Prompt variant (if applicable): Standard /sp.plan workflow with constitution conflict resolution
- Next experiment (smallest change to try): Create ADR for dual-to-single provider decision, then proceed to task breakdown
