---
id: 0003
title: Document OpenAI-only migration ADR
stage: misc
date: 2026-02-23
surface: agent
model: Claude Opus 4.6 (1M context)
feature: 004-openai-only
branch: 004-openai-only
user: Ahmed-Ali-313
command: /sp.adr
labels: ["adr", "architecture", "openai", "api-migration"]
links:
  spec: specs/004-openai-only/spec.md
  ticket: null
  adr: history/adr/0007-migrate-from-dual-api-to-openai-only-llm-provider.md
  pr: null
files:
  - history/adr/0007-migrate-from-dual-api-to-openai-only-llm-provider.md
tests:
  - None (documentation phase)
---

## Prompt

Remove dual API support and standardize on OpenAI

## Response snapshot

Created ADR-0007 documenting the architectural decision to migrate from dual API (Gemini/OpenAI) to OpenAI-only:

**Decision Documented**:
- LLM Stack: OpenAI gpt-4o-mini for chat, text-embedding-3-small for embeddings
- Configuration: Single env var (OPENAI_API_KEY), removed GEMINI_API_KEY and LLM_PROVIDER
- Migration Strategy: Clean removal, no backward compatibility

**Consequences Analyzed**:
- Positive: Simplified config (3→1 env vars), reduced complexity (~500 lines removed), easier maintenance
- Negative: Single point of failure, vendor lock-in, potential re-indexing needed, constitution amendment required

**Alternatives Evaluated**:
- Keep dual API (rejected - unnecessary complexity)
- Deprecation path (rejected - no value for hackathon)
- Feature flag switching (rejected - contradicts simplification goal)
- Migrate to Gemini-only (rejected - OpenAI more mature)

**Relationship to Existing ADRs**:
- SUPERSEDES ADR-0002 (LLM and Vector Database Stack) - removes dual API requirement

## Outcome

- ✅ Impact: Architectural decision formally documented, ready for constitution amendment and implementation
- 🧪 Tests: No tests (ADR documentation only)
- 📁 Files: 1 ADR created (0007-migrate-from-dual-api-to-openai-only-llm-provider.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, then update constitution.md to v3.0.0
- 🧠 Reflection: ADR captures the rationale for simplification and supersedes previous dual API decision, providing clear justification for constitution amendment

## Evaluation notes (flywheel)

- Failure modes observed: None - ADR creation successful
- Graders run and results (PASS/FAIL): Significance checklist PASS (impacts architecture, alternatives considered, cross-cutting concern)
- Prompt variant (if applicable): Standard /sp.adr workflow
- Next experiment (smallest change to try): Proceed to task breakdown, ensure constitution amendment is included in tasks
