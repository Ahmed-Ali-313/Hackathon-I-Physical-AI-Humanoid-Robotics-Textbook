---
id: 002
title: Amend Constitution Documentation-First Principle
stage: constitution
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: ahmeddev
command: /sp.constitution
labels: ["constitution", "amendment", "documentation", "research", "best-practices"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history.md
tests:
  - N/A (documentation only)
---

## Prompt

update the constition to add one more thing

always read the updated official  documentation before working on any thing like for chatbot read open ai agent sdk official documentation and so on

## Response snapshot

Amended constitution from v1.0.0 to v1.1.0 (MINOR bump) by adding Principle VIII: Documentation-First Research (NON-NEGOTIABLE).

**New Principle VIII Requirements:**
- MUST consult official documentation before implementing any feature or integration
- Specific documentation sources identified for each technology:
  - OpenAI Agents SDK (chatbot)
  - Qdrant Cloud (RAG/vector database)
  - Better-Auth (authentication)
  - FastAPI (backend)
  - Neon Serverless Postgres (database)
  - Docusaurus (frontend/book)

**Rationale:** Official documentation contains the most current APIs, best practices, and breaking changes. Relying on outdated knowledge or assumptions leads to implementation errors, deprecated API usage, and technical debt.

**Process Defined:**
1. Identify the technology/library to be used
2. Locate and read the official documentation (latest stable version)
3. Note any breaking changes, deprecations, or recommended patterns
4. Document key findings in the feature plan
5. Only then proceed with implementation

**Updates Made:**
- Feature Development Cycle: Added step 2 "Documentation Research" before planning
- Quality Gates: Added requirement "Official documentation consulted and referenced in plan"
- Version: 1.0.0 → 1.1.0 (MINOR bump - new principle added)
- Sync Impact Report: Updated to reflect changes

## Outcome

- ✅ Impact: Constitution now enforces documentation-first approach, reducing risk of using deprecated APIs or incorrect patterns
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Updated constitution.md (v1.1.0), history.md
- 🔁 Next prompts: Initialize Docusaurus project, create first feature spec, set up project structure
- 🧠 Reflection: This principle addresses a critical gap - ensuring implementations use current, official APIs rather than outdated or assumed patterns. Particularly important for rapidly evolving technologies like OpenAI Agents SDK.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution amendment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate this principle during first feature implementation to ensure it's practical and doesn't create unnecessary friction
