---
id: 0003
title: Urdu Translation Implementation Plan
stage: plan
date: 2026-02-28
surface: agent
model: claude-opus-4-6
feature: 005-urdu-translation
branch: 005-urdu-translation
user: ahmeddev
command: /sp.plan
labels: ["plan", "urdu-translation", "architecture", "openai", "rtl", "caching", "optimistic-locking"]
links:
  spec: /mnt/e/ai-native-book/specs/005-urdu-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-urdu-translation/plan.md
 - specs/005-urdu-translation/research.md
 - specs/005-urdu-translation/data-model.md
 - specs/005-urdu-translation/contracts/api-contracts.md
 - specs/005-urdu-translation/contracts/prompts.md
 - specs/005-urdu-translation/quickstart.md
 - CLAUDE.md (updated with new technology)
tests:
 - None (planning phase)
---

## Prompt

/sp.plan (no additional input - systematic architecture planning)

## Response snapshot

Completed comprehensive implementation plan for Urdu Translation feature with Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts.

**Phase 0: Research (6 technical decisions resolved)**:
1. OpenAI Translation Prompt Engineering - GPT-4o-mini with structured prompts
2. Semantic Chunking Strategy - Chunk by markdown headers for chapters >10,000 words
3. Optimistic Locking for Concurrent Translations - Version field to avoid lock contention
4. Structural Validation Criteria - Validate headers, code blocks, LaTeX, markdown parsing
5. RTL Layout Implementation - CSS direction: rtl with selective exceptions
6. Font Loading Strategy - Google Fonts CDN (Noto Nastaliq Urdu + Noto Sans Arabic)

**Phase 1: Design & Contracts (4 artifacts created)**:
1. Data Model - 2 entities (TranslatedChapter, User extended), database schema, validation rules
2. API Contracts - 5 endpoints (translate, get cached, update preference, get preference, admin invalidate)
3. Translation Prompts - OpenAI prompt templates (base, beginner, advanced, retry, chunked)
4. Quickstart Guide - Setup instructions, development workflow, testing procedures

**Constitution Check**: ✅ All 15 applicable principles satisfied

**Technical Context**:
- Language: Python 3.12 (backend), TypeScript 5.x (frontend)
- Database: Neon Serverless Postgres with optimistic locking
- Translation: OpenAI GPT-4o-mini with structured prompts
- Performance: <5s first-time, <500ms cached, 80%+ cache hit rate target
- RTL Layout: CSS direction property with Noto Nastaliq Urdu font

## Outcome

- ✅ Impact: Complete architecture plan with research, data model, API contracts, prompts, and quickstart guide
- 🧪 Tests: None (planning phase - tests will be defined in tasks phase)
- 📁 Files: 7 files created (plan.md, research.md, data-model.md, api-contracts.md, prompts.md, quickstart.md, CLAUDE.md updated)
- 🔁 Next prompts: /sp.tasks (generate prioritized task list with test scenarios for each user story)
- 🧠 Reflection: Planning phase complete with all technical decisions resolved, constitution compliance verified, and comprehensive documentation. Architecture uses proven patterns (optimistic locking, cache-first strategy, semantic chunking) aligned with constitution principles. Ready for task breakdown and TDD implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASSED (all 15 applicable principles satisfied)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task breakdown phase to generate implementation tasks with TDD approach
