---
id: 001
title: Create Project Constitution
stage: constitution
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: ahmeddev
command: /sp.constitution
labels: ["constitution", "initialization", "principles", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history.md
  - guide.md
tests:
  - N/A (documentation only)
---

## Prompt

/sp.constitution

always make the ui first so you can check api handling
do unit test
always create a history.md file for the whoe project so when ever you visit the the project you just read the file and know where you end it prevent the token burn

write the remaining constitution according to the project

## Response snapshot

Created comprehensive constitution (v1.0.0) for Physical AI & Humanoid Robotics hackathon project with 7 core principles:

1. **Deliverables-First (NON-NEGOTIABLE)**: All work must map to one of 5 hackathon deliverables (textbook, RAG chatbot, auth system, personalization, demo video)

2. **UI-First Development (NON-NEGOTIABLE)**: Build UI components with mock data before implementing backend APIs to ensure API contracts are driven by actual UI needs

3. **Mandatory Unit Testing (NON-NEGOTIABLE)**: Every component must have unit tests with minimum 80% coverage for critical paths before being considered complete

4. **Project History Tracking (NON-NEGOTIABLE)**: history.md file must be maintained at project root, updated after every work session to prevent token burn and provide instant context

5. **Tech Stack Compliance**: Locked to hackathon requirements (Docusaurus, FastAPI, Qdrant, Neon Postgres, Better-Auth, OpenAI Agents)

6. **Content Completeness**: Textbook must cover all 4 modules (ROS 2, Gazebo/Unity, NVIDIA Isaac, VLA) plus hardware chapters

7. **Deployment Readiness**: All components must be production-ready with no hardcoded secrets, documented dependencies, and tested deployment

Additional sections created:
- Development Workflow (10-step feature development cycle)
- Quality Gates (7 mandatory checks before PR merge)
- Git Workflow (branch naming, commit conventions)
- Documentation Requirements (5 required files including history.md)
- Security & Privacy (authentication, data handling, API security)
- Performance Standards (frontend, backend, resource constraints)
- Governance (amendment process, compliance verification, versioning)

## Outcome

- ✅ Impact: Constitution v1.0.0 ratified, establishing foundational principles for hackathon project development
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Created constitution.md, history.md; updated guide.md
- 🔁 Next prompts: Initialize Docusaurus project, create first feature spec, set up project structure
- 🧠 Reflection: Constitution successfully captures user's key requirements (UI-first, unit testing, history tracking) while incorporating hackathon deliverables and tech stack constraints. The history.md principle addresses token burn concern directly.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (initial constitution creation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution principles during first feature implementation to ensure they're practical and enforceable
