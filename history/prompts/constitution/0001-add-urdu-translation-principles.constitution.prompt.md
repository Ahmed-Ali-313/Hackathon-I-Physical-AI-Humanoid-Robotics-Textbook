---
id: 0001
title: Add Urdu Translation Principles
stage: constitution
date: 2026-02-28
surface: agent
model: claude-opus-4-6
feature: none
branch: 003-rag-chatbot
user: ahmeddev
command: /sp.constitution
labels: ["constitution", "urdu-translation", "internationalization", "i18n", "rtl", "tdd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution amendment)
---

## Prompt

now i want to move on phase 4 urdu translations of the the whole book content, help me writin the constitution abput it and then we will write the specs, check the constitution that it has rules about it or not? if not so we will write/updaate the constituiotn first

Principle I: User-Centric Accessibility
- Translation Trigger: The translation must be initiated by the logged-in user through a dedicated button located at the start of each chapter.
- State Management: The system must remember the user's language preference across different chapters once the button is toggled.
- Authentication Dependency: As a bonus feature, the translation functionality is strictly reserved for users who have successfully signed up and logged in.

Principle II: Technical & Linguistic Fidelity
- Preservation of Terms: To maintain the technical integrity of the "Physical AI & Humanoid Robotics" course, all core technical terms (e.g., ROS 2, VSLAM, URDF, Kinematics, SLAM) must remain in English.
- Translation Engine: The system shall use the OpenAI API as the primary engine for high-context, technical translation.
- Contextual Accuracy: The translation must reflect the academic tone of the Panaversity curriculum, avoiding generic or literal translations of programming concepts.

Principle III: Structural Integrity (Markdown & Code)
- Code Block Immunity: All code blocks, terminal commands, and inline code must be excluded from translation.
- Mathematical Preservation: LaTeX equations and mathematical symbols must remain untouched to ensure scientific accuracy.
- Markdown Syntax: Headers, lists, and image links must retain their Markdown structure.

Principle IV: Performance & Caching
- Database Integration: To minimize API latency and costs, successfully translated chapters must be cached in the Neon Serverless Postgres database.
- Inference Optimization: The backend (FastAPI) must check for a cached Urdu version before requesting a new translation from OpenAI.

Principle V: UI/UX & RTL Standards
- Visual Direction: When the Urdu mode is active, the content container must dynamically switch to a Right-to-Left (RTL) layout.
- Font Legibility: The Urdu text must utilize a professional typeface (like Noto Nastaliq Urdu) with a line-height of at least 1.8.
- No Page Reload: The transition between English and Urdu should be handled via React state.

ADDITIONAL: always use test driven development apporach

## Response snapshot

Constitution updated from TEMPLATE → v4.0.0 (MAJOR version bump).

Added 5 comprehensive principles for Urdu translation & internationalization (Principles XI-XV):
- User-centric translation accessibility with authentication
- Technical & linguistic fidelity with term preservation
- Structural integrity for markdown & code
- Translation performance & caching strategy
- UI/UX & RTL standards

Strengthened Principle III: ALWAYS Use Test-Driven Development (NON-NEGOTIABLE) with mandatory enforcement.

Added technology stack requirements: Noto Nastaliq Urdu fonts, translation caching schema, user preferences extension.

Added development workflow section for translation feature testing (unit, integration, E2E, manual).

## Outcome

- ✅ Impact: Constitution v4.0.0 ratified with comprehensive Urdu translation & internationalization architecture
- 🧪 Tests: None (constitution document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create Phase 4 Urdu Translation specification)
- 🧠 Reflection: MAJOR version bump justified by adding mandatory internationalization architecture with RTL support, caching requirements, and authentication constraints. TDD principle strengthened to enforce test-first approach.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution amendment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase 4 specification following new Urdu translation principles
