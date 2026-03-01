<!--
Sync Impact Report:
Version: 3.0.0 → 3.1.0 (MINOR)
Rationale: Added Phase 5 deployment and infrastructure principles for production readiness
Modified Principles: None (existing principles unchanged)
Added Sections:
  - Principle XI: Deployment & Infrastructure (4 sub-principles)
    - A. Architectural Separation (The Hybrid Rule)
    - B. Security & Credential Integrity
    - C. Network & Communication Protocols
    - D. Deployment Safety & Rollback
Updated Sections:
  - Tech Stack Requirements: Clarified Render as primary backend deployment platform
  - Deployment Architecture: Added Neon database migration guidance
Templates Requiring Updates:
  - ✅ .specify/templates/plan-template.md (deployment plans reference Render + Vercel)
  - ✅ .specify/templates/tasks-template.md (deployment tasks include Neon migration)
  - ⚠ .specify/templates/spec-template.md (deployment specs may need infrastructure section)
Deployment Readiness:
  - ✅ Frontend deployment strategy defined (Vercel)
  - ✅ Backend deployment strategy defined (Render)
  - ✅ Database migration path defined (SQLite → Neon)
  - ✅ Security requirements documented (environment variables, CORS)
  - ✅ CI/CD automation requirements specified
Follow-up TODOs:
  - Create deployment specification (Phase 5)
  - Create deployment plan with Neon migration steps
  - Create deployment tasks with safety checks
-->

# AI-Native Textbook Constitution

## Core Principles

### I. UI-First Development
All user interface components MUST be built and validated before implementing backend APIs.

**Rationale**: Ensures user experience drives technical decisions, prevents over-engineering backend features that users don't need, and allows early user feedback on workflows.

**Requirements**:
- Design and implement all frontend pages, forms, and components first
- Create mockups or wireframes for complex interactions
- Validate UI flows with stakeholders before API development
- Backend APIs are built to serve the UI's actual needs, not assumed requirements

### II. Mandatory Unit Testing
80% test coverage is REQUIRED for all critical paths. Tests MUST be written before implementation (TDD).

**Rationale**: Prevents regressions, documents expected behavior, enables confident refactoring, and ensures code quality from the start.

**Requirements**:
- Write tests first (Red-Green-Refactor cycle)
- Critical paths: authentication, data persistence, business logic, API endpoints
- Tests must be independent, repeatable, and fast
- Integration tests required for cross-service communication
- Mock external dependencies (databases, APIs, third-party services)

### III. History Tracking
The `history.md` file MUST be updated at the end of every development session.

**Rationale**: Prevents token burn by providing context for future sessions, documents decisions and rationale, and creates an audit trail of project evolution.

**Requirements**:
- Update history.md before ending each session
- Include: work completed, files modified, key decisions, current status, next steps
- Use consistent date format (YYYY-MM-DD)
- Document blockers and their resolutions
- Record token usage for major sessions

### IV. Deliverables-First
All work MUST map to one of the five hackathon deliverables.

**Rationale**: Maintains focus on project goals, prevents scope creep, and ensures all effort contributes to demonstrable outcomes.

**Deliverables**:
1. AI-Native Technical Textbook (Docusaurus)
2. Integrated RAG Chatbot (OpenAI Agents SDK + Qdrant + FastAPI)
3. Authentication System (Better-Auth)
4. Personalization & Translation Features
5. Demo Video (90 seconds max)

**Requirements**:
- Every feature must explicitly state which deliverable it supports
- Reject work that doesn't advance a deliverable
- Prioritize P1 deliverables (textbook, chatbot) over bonus features

### V. Tech Stack Compliance
The following technology stack is MANDATORY and non-negotiable.

**Rationale**: Hackathon requirements, ensures consistency, leverages proven tools, and meets evaluation criteria.

**Required Technologies**:
- **Frontend**: Docusaurus 3.x, React 19, TypeScript
- **Backend**: FastAPI (Python), async/await patterns
- **Databases**:
  - Neon Serverless Postgres (structured data, chat history, user sessions)
  - Qdrant Cloud Free Tier (vector embeddings, semantic search)
- **Authentication**: Better-Auth (JWT-based)
- **AI/LLM**: OpenAI Agents SDK (chatbot logic and capabilities)
- **Deployment**: Vercel (frontend), Render (backend)
- **Development**: Claude Code, Spec-Kit Plus

**Prohibited**:
- No alternative frameworks without explicit approval
- No local-only databases in production
- No hardcoded API keys or secrets

### VI. Documentation-First Research
Official documentation MUST be consulted before implementing any feature using external libraries or frameworks.

**Rationale**: Prevents misuse of APIs, reduces debugging time, ensures best practices, and avoids deprecated patterns.

**Requirements**:
- Read official docs for: OpenAI Agents SDK, Qdrant, Better-Auth, FastAPI, Neon, Docusaurus
- Reference documentation in implementation plans
- Use official examples as starting points
- Verify API compatibility and version requirements
- Document any deviations from official patterns with justification

### VII. Dependency Installation
All dependencies MUST be installed before running or testing code.

**Rationale**: Prevents runtime crashes, ensures reproducible environments, and catches dependency conflicts early.

**Requirements**:
- Run `npm install` after cloning or pulling frontend changes
- Run `pip install -r requirements.txt` (or `poetry install`) after backend changes
- Install dependencies before running dev servers
- Install dependencies before running tests
- Install dependencies before building for production
- Document all dependency changes in commit messages

### VIII. Smallest Viable Change
Prefer minimal, focused changes over comprehensive refactoring.

**Rationale**: Reduces risk, simplifies code review, enables faster iteration, and prevents scope creep.

**Requirements**:
- One feature per branch/PR
- No unrelated refactoring in feature branches
- No "while we're here" improvements
- Extract reusable code only when needed 3+ times
- Avoid premature abstractions

### IX. Code Quality Standards
All code MUST meet minimum quality standards before merging.

**Rationale**: Maintains codebase health, prevents technical debt, and ensures long-term maintainability.

**Requirements**:
- No hardcoded secrets or API keys (use environment variables)
- Proper error handling with user-friendly messages
- Type hints for Python, TypeScript for JavaScript
- Consistent code formatting (Black for Python, Prettier for TypeScript)
- Meaningful variable and function names
- Comments only for non-obvious logic
- No commented-out code in commits

### X. RAG Chatbot Architecture

The RAG (Retrieval-Augmented Generation) chatbot MUST follow these architectural principles to ensure accurate, grounded, and course-specific responses.

**Rationale**: Students need reliable, textbook-grounded answers. Generic LLM responses can hallucinate or provide information inconsistent with course material. RAG ensures responses are anchored in the actual textbook content.

#### A. Strict RAG Grounding (MANDATORY)
The chatbot MUST prioritize information retrieved from the textbook over its general training data.

**Requirements**:
- Retrieve relevant textbook chunks from Qdrant before generating responses
- Include retrieved context in the prompt to the LLM
- Configure the LLM to explicitly prefer retrieved content over general knowledge
- Implement confidence scoring for retrieved chunks (minimum threshold: 0.7)
- If no relevant content found above threshold, state limitations clearly

**Implementation Pattern**:
```
1. User asks question
2. Generate embedding for question
3. Query Qdrant for top-k relevant chunks (k=5)
4. Filter chunks by confidence score (>0.7)
5. If chunks found: Include in LLM prompt with instruction to prioritize
6. If no chunks: Respond "I don't have information about this in the textbook"
```

#### B. Source Attribution (MANDATORY)
All chatbot responses MUST include references to the specific textbook sections used.

**Requirements**:
- Store chapter/section metadata with each vector embedding
- Return source references alongside retrieved chunks
- Display clickable links to source chapters in the UI
- Format: "Source: [Chapter Name](URL) - Section X.Y"
- Show multiple sources if answer draws from multiple sections

#### C. Selection-Based Context (REQUIRED)
The chatbot MUST support answering questions based on user-selected text.

**Rationale**: Allows students to ask specific questions about complex passages without the chatbot searching the entire textbook.

**Requirements**:
- Detect when user has text selected in the browser
- Provide "Ask about selection" mode in the UI
- Use selected text as primary context (skip Qdrant retrieval)
- Still include source attribution for the selected section
- Fall back to full RAG if no text selected

#### D. Uncertainty Handling (MANDATORY)
The chatbot MUST explicitly state when it cannot answer based on textbook content.

**Requirements**:
- Never hallucinate facts about Physical AI, robotics, or course topics
- Use phrases like: "I don't have information about this in the textbook"
- Suggest related topics that ARE covered in the textbook
- Offer to search for related content
- Do NOT provide general knowledge answers for course-specific questions

**Prohibited Responses**:
- ❌ "Based on my knowledge..." (when not in textbook)
- ❌ Making up ROS 2 commands not in the textbook
- ❌ Inventing NVIDIA Isaac Sim features not documented
- ❌ Providing hardware specs not mentioned in the course

#### E. Tone and Pedagogy (REQUIRED)
The chatbot MUST maintain an academic yet encouraging tone suitable for technical education.

**Requirements**:
- Professional and respectful language
- Break down complex concepts (VSLAM, Bipedal Locomotion, DDS) into steps
- Use analogies when helpful for understanding
- Encourage further exploration of topics
- Acknowledge when topics are advanced and suggest prerequisites
- Avoid overly casual language or emojis (unless user explicitly requests)

**Example Tone**:
- ✅ "VSLAM (Visual Simultaneous Localization and Mapping) works by..."
- ✅ "Let's break down bipedal locomotion into three key phases..."
- ✅ "This is an advanced topic. You might want to review Chapter 2 on ROS 2 basics first."
- ❌ "Yo! VSLAM is super cool! 🤖"
- ❌ "That's way too hard for you right now."

### XI. Deployment & Infrastructure

The production deployment MUST follow a hybrid architecture strategy to ensure reliability, performance, and cost-effectiveness while maintaining development flexibility.

**Rationale**: Different components have different hosting requirements. Static frontends benefit from CDN distribution (Vercel), while backends with long-running processes need persistent servers (Render). Separating concerns enables optimal platform selection while maintaining monorepo cohesion.

#### A. Architectural Separation (The Hybrid Rule)

**Frontend Sovereignty**: The Docusaurus textbook SHALL be hosted on Vercel as a static site to ensure global high-speed access for readers.

**Requirements**:
- Deploy frontend to Vercel with automatic CI/CD from GitHub
- Use Vercel's edge network for global content delivery
- Configure custom domain if available
- Enable automatic preview deployments for pull requests
- Set `REACT_APP_API_URL` environment variable to point to production backend

**Backend Persistence**: The FastAPI backend SHALL be hosted on Render (Web Service) to support long-running processes like Urdu translation and AI streaming, bypassing Vercel's 10-second execution limit.

**Requirements**:
- Deploy backend to Render as a Web Service (not serverless)
- Configure health check endpoint (`/api/health`) for monitoring
- Enable automatic deployments from GitHub
- Use Render's persistent connections for Qdrant and Neon
- Configure environment variables for all secrets (OpenAI, Qdrant, Neon, JWT)

**Monorepo Cohesion**: Despite being on two platforms, the codebase MUST remain in a single GitHub repository, using platform-specific configuration files (`vercel.json` and `render.yaml`) to define their respective environments.

**Requirements**:
- Maintain single GitHub repository with `/backend` and `/textbook` directories
- Create `vercel.json` in `/textbook` directory for Vercel configuration
- Create `render.yaml` in project root for Render configuration
- Use `.gitignore` to exclude platform-specific build artifacts
- Document deployment process in `README.md`

#### B. Security & Credential Integrity

**Zero-Leakage Policy**: No API keys (OpenAI, Qdrant) or database strings (Neon) SHALL be hardcoded. They MUST be fetched via `os.getenv()` in Python and `process.env` in JavaScript.

**Requirements**:
- All secrets stored in environment variables
- Use `.env` files for local development (never commit to Git)
- Use `.env.example` files to document required variables
- Validate required environment variables on application startup
- Log missing environment variables with clear error messages

**Automated Secret Sync**: The agent SHALL use the GitHub CLI (`gh`) to sync local `.env` values to GitHub Secrets, ensuring CI/CD pipelines have immediate access to necessary credentials.

**Requirements**:
- Use `gh secret set` to add secrets to GitHub repository
- Sync secrets before enabling CI/CD deployments
- Document all required secrets in deployment guide
- Rotate secrets periodically (every 90 days minimum)
- Never log or expose secret values in application logs

**Database Isolation**: The production environment MUST connect exclusively to Neon Serverless Postgres, while the local environment retains a SQLite fallback for offline development.

**Requirements**:
- Production: `DATABASE_URL=postgresql://...@neon.tech/...`
- Local development: `DATABASE_URL=sqlite+aiosqlite:///./ai_native_book.db`
- Use SQLAlchemy's engine configuration to support both dialects
- Run migrations on both databases to ensure schema parity
- Document database setup in `README.md` and deployment guide

#### C. Network & Communication Protocols

**Cross-Origin Resource Sharing (CORS)**: The Render backend MUST explicitly whitelist the production Vercel URL to allow the RAG chatbot to function across domains.

**Requirements**:
- Configure CORS middleware in FastAPI `main.py`
- Whitelist production Vercel URL (e.g., `https://ai-native-book.vercel.app`)
- Whitelist localhost URLs for local development (`http://localhost:3001`)
- Allow credentials for JWT authentication (`allow_credentials=True`)
- Restrict allowed methods and headers to minimum required

**Example Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "https://ai-native-book.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Health Check Resilience**: Because the Render free tier "spins down" after 15 minutes of inactivity, the frontend MUST implement a "Waking Up" status indicator to manage user expectations during the 30-second cold start.

**Requirements**:
- Implement health check polling in frontend (`/api/health` endpoint)
- Show "Connecting to server..." message during cold start
- Retry failed requests with exponential backoff
- Display user-friendly error messages for prolonged downtime
- Consider implementing a "wake-up" ping on page load

**Dependency Locking**: Every deployment MUST verify that `backend/requirements.txt` includes `psycopg2-binary` for Postgres and `python-dotenv` for environment management.

**Requirements**:
- `psycopg2-binary>=2.9.0` for Neon Postgres connectivity
- `python-dotenv>=1.0.0` for `.env` file loading
- Pin all dependency versions to prevent breaking changes
- Run `pip freeze > requirements.txt` after adding dependencies
- Test deployment with fresh virtual environment

#### D. Deployment Safety & Rollback

**Atomic Deploys**: No code SHALL be pushed to the main branch unless it has passed a local linting and "Dry Run" start sequence.

**Requirements**:
- Run linting before commit: `black backend/src` and `prettier --write textbook/src`
- Test backend startup: `cd backend && uvicorn src.main:app --reload`
- Test frontend build: `cd textbook && npm run build`
- Run test suite: `pytest backend/tests/` and `npm test` (if applicable)
- Verify all environment variables are documented in `.env.example`

**Stateful Protection**: During the database migration to Neon, the agent MUST perform a "Schema Check" to ensure existing user tables are not dropped or damaged during the synchronization.

**Requirements**:
- Backup local SQLite database before migration: `cp ai_native_book.db ai_native_book.db.backup`
- Export schema from SQLite: `sqlite3 ai_native_book.db .schema > schema_backup.sql`
- Run migrations on Neon in a transaction (rollback on error)
- Verify table counts match: `SELECT COUNT(*) FROM users;` on both databases
- Test authentication and core features after migration
- Keep SQLite backup for 7 days after successful migration

**Rollback Strategy**: If production deployment fails, the agent MUST be able to revert to the previous working version within 5 minutes.

**Requirements**:
- Use Vercel's rollback feature: `vercel rollback` or via dashboard
- Use Render's rollback feature: redeploy previous commit via dashboard
- Document rollback procedure in deployment guide
- Test rollback procedure in staging environment
- Monitor error logs for 24 hours after deployment

## Tech Stack Requirements

### Backend Architecture
**Framework**: FastAPI (Python 3.11+)
- Async/await patterns for all I/O operations
- Pydantic models for request/response validation
- Dependency injection for database sessions
- CORS configuration for Docusaurus frontend

**Databases**:
- **Neon Serverless Postgres**: User accounts, chat history, user sessions, preference data
  - Connection pooling: `pool_size=5, max_overflow=10`
  - SSL mode: `sslmode=require`
  - Connection string format: `postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require`
- **Qdrant Cloud (Free Tier)**: Document embeddings (768-dim vectors), metadata (chapter, section, page)

**AI/LLM**:
- **OpenAI API (MANDATORY)**: The chatbot uses OpenAI API exclusively for simplified architecture
  - **Model**: gpt-4o-mini for chat completion and response generation
  - **Embeddings**: text-embedding-3-small (768-dimensional vectors)
  - **Configuration**: Single environment variable (OPENAI_API_KEY)
- **Implementation Pattern**:
  ```python
  # OpenAI-only configuration
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  ```
- **Rationale**: Simplified configuration, reduced complexity, single API to maintain

**Authentication**:
- **Better-Auth**: JWT token generation and validation
- Session management in Neon Postgres
- Secure password hashing (bcrypt)

### Frontend Architecture
**Framework**: Docusaurus 3.x
- React 19 components
- TypeScript for type safety
- CSS Modules for styling

**Chatbot UI Integration**:
- Embedded as a Docusaurus theme component
- Floating chat button (bottom-right corner)
- Expandable chat panel (overlay or sidebar)
- Markdown rendering for bot responses
- Clickable source links to textbook chapters
- "Ask about selection" button when text is selected

### Deployment Architecture
**Frontend**: Vercel
- Automatic deployments from Git (main branch)
- Preview deployments for PRs
- Environment variables for API endpoints (`REACT_APP_API_URL`)
- Custom domain support
- Edge network for global CDN

**Backend**: Render (Web Service)
- Automatic deployments from Git (main branch)
- Environment variables for secrets (OpenAI API key, database URLs, JWT secret)
- Health check endpoint for monitoring (`/api/health`)
- Free tier: 750 hours/month, spins down after 15 min inactivity
- Persistent connections to Neon and Qdrant

**Databases**:
- **Neon Postgres**: Managed, serverless, auto-scaling
  - Free tier: 0.5GB storage, 1 project
  - Connection pooling built-in
  - Automatic backups
- **Qdrant Cloud**: Managed, free tier (1GB storage, 100k vectors)
  - REST API access
  - Persistent storage
  - Automatic scaling

**CI/CD Pipeline**:
- GitHub Actions (optional) for automated testing
- Automatic deployments on push to main branch
- Preview deployments for pull requests
- Environment-specific configurations (staging, production)

## Feature Development Cycle

1. **Specification** (`/sp.specify`)
   - Define WHAT users need and WHY
   - No implementation details
   - Measurable success criteria
   - Map to deliverables

2. **Clarification** (`/sp.clarify`) - Optional
   - Resolve ambiguities in spec
   - Maximum 3 clarification questions
   - Update spec with answers

3. **Planning** (`/sp.plan`)
   - Consult official documentation (Principle VI)
   - Design architecture and data models
   - Identify dependencies and risks
   - Create ADRs for significant decisions
   - Validate against constitution principles

4. **Task Breakdown** (`/sp.tasks`)
   - Generate actionable, testable tasks
   - Dependency ordering
   - Acceptance criteria for each task

5. **Implementation** (`/sp.implement`)
   - Install dependencies first (Principle VII)
   - UI-first approach (Principle I)
   - TDD with 80% coverage (Principle II)
   - Smallest viable changes (Principle VIII)
   - Code quality standards (Principle IX)

6. **Testing**
   - Unit tests (80% coverage minimum)
   - Integration tests for APIs
   - Manual testing for UI flows
   - RAG chatbot: test grounding, attribution, uncertainty handling

7. **Documentation**
   - Update history.md (Principle III)
   - Create PHR for the session
   - Update README if needed
   - Document API endpoints

8. **Commit & PR**
   - Descriptive commit messages
   - Reference issue/task numbers
   - Co-authored by Claude Opus 4.6

## Quality Gates

All pull requests MUST pass these gates before merging:

### Code Quality
- [ ] No hardcoded secrets or API keys
- [ ] All dependencies installed and documented
- [ ] Type hints (Python) or TypeScript (frontend)
- [ ] Consistent formatting (Black, Prettier)
- [ ] No commented-out code

### Testing
- [ ] 80% test coverage for critical paths
- [ ] All tests passing
- [ ] Integration tests for new APIs
- [ ] Manual testing completed for UI changes

### Documentation
- [ ] history.md updated with session details
- [ ] PHR created for the session
- [ ] Official documentation consulted and referenced
- [ ] README updated if setup changed

### Constitution Compliance
- [ ] Maps to a deliverable (Principle IV)
- [ ] Uses required tech stack (Principle V)
- [ ] UI-first approach followed (Principle I)
- [ ] Smallest viable change (Principle VIII)
- [ ] RAG chatbot follows grounding principles (Principle X)

### RAG Chatbot Specific
- [ ] Retrieves from Qdrant before generating responses
- [ ] Includes source attribution with clickable links
- [ ] Handles uncertainty explicitly (no hallucination)
- [ ] Supports selection-based context mode
- [ ] Maintains academic tone

### Deployment Readiness (Phase 5+)
- [ ] Environment variables documented in `.env.example`
- [ ] CORS configured for production URLs
- [ ] Database migrations tested on Neon
- [ ] Health check endpoint implemented
- [ ] Rollback procedure documented

## Governance

This constitution supersedes all other development practices and guidelines.

**Amendment Process**:
1. Propose amendment with rationale
2. Document impact on existing code and templates
3. Update version number (semantic versioning)
4. Update all dependent templates and documentation
5. Create PHR documenting the amendment
6. Commit with message: `docs: amend constitution to vX.Y.Z (description)`

**Version Policy**:
- **MAJOR**: Backward-incompatible changes (removing principles, changing tech stack)
- **MINOR**: New principles or sections added
- **PATCH**: Clarifications, wording improvements, typo fixes

**Compliance Review**:
- All PRs must demonstrate constitution compliance
- Violations must be justified and documented
- Repeated violations require constitution amendment or code changes

**Conflict Resolution**:
- Constitution principles override project preferences
- When principles conflict, prioritize in order: I → XI
- Unresolved conflicts require user decision

**Runtime Guidance**:
- See `CLAUDE.md` for agent-specific development guidance
- See `guide.md` for hackathon requirements and deliverables
- See `history.md` for project evolution and decisions

---

**Version**: 3.1.0 | **Ratified**: 2026-02-16 | **Last Amended**: 2026-03-02
