---
id: 0002
title: Update constitution Phase 5 deployment
stage: constitution
date: 2026-03-02
surface: agent
model: claude-opus-4-6
feature: none
branch: 005-urdu-translation
user: ahmeddev
command: /sp.constitution
labels: ["constitution", "deployment", "phase-5", "infrastructure", "vercel", "render", "neon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation only)
---

## Prompt

now first we have to update the constitution for the phase 5 deployment and then we make specs and then plan task so the svery thing move smootly and systemetically

Phase 5: Hybrid Deployment & Infrastructure Constitution
Principle I: Architectural Separation (The Hybrid Rule)
Frontend Sovereignty: The Docusaurus textbook shall be hosted on Vercel as a static site to ensure global high-speed access for readers.

Backend Persistence: The FastAPI backend shall be hosted on Render (Web Service) to support long-running processes like Urdu translation and AI streaming, bypassing Vercel's 10-second execution limit.

Monorepo Cohesion: Despite being on two platforms, the codebase must remain in a single GitHub repository, using platform-specific configuration files (vercel.json and render.yaml) to define their respective environments.

Principle II: Security & Credential Integrity
Zero-Leakage Policy: No API keys (OpenAI, Qdrant) or database strings (Neon) shall be hardcoded. They must be fetched via os.getenv() in Python and process.env in JavaScript.

Automated Secret Sync: The agent shall use the GitHub CLI (gh) to sync local .env values to GitHub Secrets, ensuring CI/CD pipelines have immediate access to necessary credentials.

Database Isolation: The production environment must connect exclusively to Neon Serverless Postgres, while the local environment retains a SQLite fallback for offline development.

Principle III: Network & Communication Protocols
Cross-Origin Resource Sharing (CORS): The Render backend must explicitly whitelist the production Vercel URL to allow the RAG chatbot to function across domains.

Health Check Resilience: Because the Render free tier "spins down" after 15 minutes of inactivity, the frontend must implement a "Waking Up" status indicator to manage user expectations during the 30-second cold start.

Dependency Locking: Every deployment must verify that backend/requirements.txt includes psycopg2-binary for Postgres and python-dotenv for environment management.

Principle IV: Deployment Safety & Rollback
Atomic Deploys: No code shall be pushed to the main branch unless it has passed a local linting and "Dry Run" start sequence.

Stateful Protection: During the database migration to Neon, the agent must perform a "Schema Check" to ensure existing user tables are not dropped or damaged during the synchronization.

update the constituitons using the context for the phase 5 and then let me know

also save the work after some time

## Response snapshot

Updated constitution from v3.0.0 to v3.1.0 (MINOR version bump) by adding Principle XI: Deployment & Infrastructure with four comprehensive sub-principles:

**A. Architectural Separation (The Hybrid Rule)**
- Frontend on Vercel (static site, global CDN)
- Backend on Render (Web Service for long-running processes)
- Monorepo with platform-specific configs (vercel.json, render.yaml)

**B. Security & Credential Integrity**
- Zero-Leakage Policy: All secrets via environment variables
- Automated Secret Sync: GitHub CLI for secret management
- Database Isolation: Neon (production) vs SQLite (local development)

**C. Network & Communication Protocols**
- CORS configuration for cross-domain communication
- Health check resilience with "Waking Up" indicator for Render cold starts
- Dependency locking: psycopg2-binary and python-dotenv required

**D. Deployment Safety & Rollback**
- Atomic deploys with linting and dry-run checks
- Stateful protection during Neon migration with schema verification
- Rollback strategy documented

Also updated Tech Stack Requirements section to clarify Render as primary backend platform and added deployment architecture details including Neon connection pooling configuration.

## Outcome

- ✅ Impact: Constitution v3.1.0 ratified with Phase 5 deployment principles, establishing production deployment standards for Vercel + Render + Neon architecture
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Updated .specify/memory/constitution.md (v3.0.0 → v3.1.0)
- 🔁 Next prompts: Create Phase 5 deployment specification (/sp.specify), create deployment plan (/sp.plan), create deployment tasks (/sp.tasks)
- 🧠 Reflection: Constitution successfully captures hybrid deployment architecture requirements while maintaining security, safety, and rollback guarantees. The principles are concrete and testable, providing clear guidance for production deployment without compromising development flexibility.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution amendment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate deployment principles during Phase 5 implementation to ensure they're practical and cover all edge cases (Neon migration, CORS configuration, cold start handling)
