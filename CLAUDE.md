# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

---

## Project Overview

**Project Name:** AI-Native Textbook - Physical AI & Embodied Intelligence

**Type:** Hackathon project building an interactive technical textbook with integrated AI assistance

**Current Phase:** Phase 3-4 (RAG Chatbot Implementation)
- Progress: 56/115 tasks complete (49%)
- Branch: `003-rag-chatbot`
- Status: Backend and frontend functionally complete for User Stories 1-2, ready for testing with credentials

**Five Deliverables:**
1. AI-Native Technical Textbook (Docusaurus) - ✅ Complete (Phase 1)
2. Integrated RAG Chatbot (OpenAI Agents SDK + Qdrant + FastAPI) - ⏳ In Progress (Phase 3-4)
3. Authentication System (Better-Auth) - ✅ Complete (Phase 2)
4. Personalization & Translation Features - ✅ Complete (Phase 2)
5. Demo Video (90 seconds max) - ⏳ Pending

## Tech Stack

**Frontend:**
- Docusaurus 3.x (static site generator)
- React 19 (UI components)
- TypeScript (type safety)
- CSS Modules (styling)

**Backend:**
- FastAPI (Python 3.11+, async/await)
- Pydantic (request/response validation)
- asyncpg (Postgres async driver)

**Databases:**
- Neon Serverless Postgres (structured data: users, chat history, sessions)
- Qdrant Cloud Free Tier (vector embeddings: 768-dim, semantic search)

**Authentication:**
- Better-Auth (JWT-based, session management)

**AI/LLM:**
- OpenAI Agents SDK (chatbot orchestration)
- Google Gemini API (primary: gemini-1.5-flash/pro)
- OpenAI API (secondary: gpt-4o-mini/gpt-4o, commented out)
- Google Generative AI embeddings (text-embedding-004)

**Deployment:**
- Vercel (frontend hosting)
- Railway/Render (backend hosting)

**Development:**
- Claude Code (AI pair programming)
- Spec-Kit Plus (SDD methodology)

## Key Files & Structure

```
ai-native-book/
├── history.md                          # Session summaries, progress tracking
├── .specify/memory/constitution.md     # Project principles (10 core principles)
├── CLAUDE.md                           # This file - agent instructions
├── specs/003-rag-chatbot/              # Current feature specs
│   ├── spec.md                         # Requirements (what & why)
│   ├── plan.md                         # Architecture (how)
│   └── tasks.md                        # Implementation tasks (115 total)
├── backend/
│   ├── src/
│   │   ├── config.py                   # RAG configuration
│   │   ├── services/                   # embedding, vector, agent, chat
│   │   ├── models/                     # Conversation, ChatMessage, ChatSession
│   │   ├── tools/                      # Agent tools (vector_search, retrieve_context)
│   │   └── api/chat.py                 # 7 REST endpoints
│   ├── scripts/
│   │   ├── create_qdrant_collection.py # Qdrant setup
│   │   └── index_textbook.py           # Textbook indexing with embeddings
│   ├── tests/                          # 180+ backend tests
│   └── requirements.txt                # Python dependencies
└── textbook/
    ├── src/
    │   ├── components/
    │   │   ├── ChatButton/             # Floating "Ask" button
    │   │   ├── ChatPanel/              # Slide-out chat interface
    │   │   ├── MessageList/            # Chat messages display
    │   │   ├── MessageInput/           # User input with 500 char limit
    │   │   ├── TypingIndicator/        # Three-dot animation
    │   │   └── SourceLink/             # Clickable chapter references
    │   ├── contexts/ChatContext.tsx    # Global chat state
    │   ├── hooks/
    │   │   ├── useChat.ts              # Chat state management
    │   │   └── useTextSelection.ts     # Text selection detection
    │   └── services/chatApi.ts         # Backend API client
    └── package.json                    # Node dependencies
```

## Development Commands

**Backend:**
```bash
# Start development server
cd backend && ./venv/bin/python -m uvicorn src.main:app --reload --port 8001

# Run tests
cd backend && pytest tests/ -v

# Run specific test file
cd backend && pytest tests/unit/test_agent_service.py -v

# Setup Qdrant collection
cd backend && python scripts/create_qdrant_collection.py

# Index textbook content
cd backend && python scripts/index_textbook.py
```

**Frontend:**
```bash
# Start development server
cd textbook && npm start -- --port 3001

# Run tests
cd textbook && npm test

# Build for production
cd textbook && npm run build
```

**Git:**
```bash
# View current status
git status

# View recent commits
git log --oneline -10

# View diff statistics
git diff --stat
```

## Project-Specific Patterns

### RAG Chatbot Architecture

**Dual API Configuration (MANDATORY):**
- Gemini API is primary (active by default in code)
- OpenAI API is secondary (commented out, ready to switch)
- Switch by commenting/uncommenting config lines + changing env vars
- No code changes beyond configuration required

**RAG Grounding Rules:**
- 0.7 confidence threshold for Qdrant vector search
- Top-5 chunks retrieved per query
- Source attribution mandatory (1-5 sources per response)
- Hallucination prevention via system prompts + uncertainty handling
- If no chunks above threshold: "I don't have information about this in the textbook"

**Two Operating Modes:**
1. **Normal Mode**: User asks question → vector search → retrieve context → generate response
2. **Selection Mode**: User highlights text → skip vector search → use selected text as context → generate focused response (confidence: 1.0)

**Response Format:**
- Content: Generated answer
- Confidence: 0.0 (no info), 0.7-1.0 (grounded)
- Sources: Array of {chapter, section, url}

**Tone & Pedagogy:**
- Professional and respectful
- Break down complex concepts (VSLAM, Bipedal Locomotion, DDS)
- Use analogies when helpful
- Encourage exploration
- Acknowledge advanced topics and suggest prerequisites
- No overly casual language or emojis

## Blocked Tasks & Credentials

**10 Tasks Currently Blocked:**

**Credential Requirements:**
- `T007`: Database migration (needs `DATABASE_URL` for Neon Postgres)
- `T010`: Textbook indexing (needs `QDRANT_URL`, `QDRANT_API_KEY`, `GEMINI_API_KEY`)
- `T009a`: Indexing validation (depends on T010)

**System Requirements (E2E Tests):**
- `T047-T048b`: User Story 1 E2E tests (needs running backend + frontend + indexed data)
- `T057-T058`: User Story 2 E2E tests (needs running system)

**Handling Strategy:**
- Document blockers in history.md
- Continue with unblocked tasks in other phases
- When credentials available, run setup scripts then unblock tests
- Never hardcode credentials; always use `.env` files

**Environment Variables Required:**
```bash
# Backend .env
DATABASE_URL=postgresql://user:pass@host/db
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key  # Optional, secondary
LLM_PROVIDER=gemini  # or "openai"
```

## Quality Gates

**Test Coverage:**
- 80% minimum for critical paths (authentication, RAG orchestration, API endpoints)
- TDD approach: write tests before implementation (Red-Green-Refactor)
- 220+ tests currently written

**Phase Completion Criteria:**
- All non-blocked tasks complete
- Tests passing
- Code follows constitution principles
- PHR created for session
- history.md updated

**Constitution Compliance:**
- UI-first development (Principle I)
- Mandatory unit testing (Principle II)
- History tracking (Principle III)
- Deliverables-first (Principle IV)
- Tech stack compliance (Principle V)
- Documentation-first research (Principle VI)
- Dependency installation (Principle VII)
- Smallest viable change (Principle VIII)
- Code quality standards (Principle IX)
- RAG chatbot architecture (Principle X)

---

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.
