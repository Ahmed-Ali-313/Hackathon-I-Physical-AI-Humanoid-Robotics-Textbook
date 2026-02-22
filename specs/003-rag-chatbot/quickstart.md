# Quickstart Guide: RAG Chatbot Integration

**Feature**: 003-rag-chatbot
**Date**: 2026-02-22
**Purpose**: Setup and development guide for RAG chatbot implementation

## Prerequisites

### Required Software
- Python 3.11+ (backend)
- Node.js 20.x LTS (frontend)
- PostgreSQL client (for Neon connection)
- Git

### Required Accounts
- **Neon Serverless Postgres**: Free tier account at https://neon.tech
- **Qdrant Cloud**: Free tier account at https://cloud.qdrant.io
- **Google AI Studio**: API key for Gemini at https://aistudio.google.com/app/apikey
- **OpenAI** (optional): API key at https://platform.openai.com/api-keys

### Existing Dependencies
- Phase 1: Textbook (17 chapters in `textbook/docs/`)
- Phase 2: Authentication system (Better-Auth, user database)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-native-book
git checkout 003-rag-chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install new dependencies for RAG chatbot
pip install qdrant-client google-generativeai openai asyncpg
```

### 3. Frontend Setup

```bash
cd textbook

# Install dependencies
npm install

# No new dependencies needed (uses existing Docusaurus + React)
```

### 4. Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database (Neon Postgres)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Vector Database (Qdrant Cloud)
QDRANT_URL=https://xxx.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key

# LLM APIs (Gemini primary, OpenAI secondary)
LLM_PROVIDER=gemini  # or "openai"
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key  # optional, for fallback

# Authentication (from Phase 2)
JWT_SECRET_KEY=your_jwt_secret_from_phase2

# CORS
CORS_ORIGINS=http://localhost:3001,http://localhost:3000

# Environment
ENVIRONMENT=development
```

Create `.env` file in `textbook/` directory:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8001
```

---

## Database Setup

### 1. Create Neon Database

1. Sign up at https://neon.tech
2. Create new project: "ai-native-book"
3. Copy connection string to `DATABASE_URL` in `.env`

### 2. Run Migrations

```bash
cd backend

# Create chat tables
python -m alembic upgrade head

# Or run SQL directly
psql $DATABASE_URL < migrations/003_create_chat_tables.sql
```

**Migration SQL** (will be created during implementation):
```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP,
    message_count INTEGER NOT NULL DEFAULT 0
);

-- chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'ai')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_references JSONB
);

-- chat_sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_messages_conversation ON chat_messages(conversation_id, created_at);
CREATE INDEX idx_sessions_user_active ON chat_sessions(user_id, is_active);
```

### 3. Setup Qdrant Collection

```bash
cd backend

# Run indexing script to create collection and index textbook
python scripts/index_textbook.py

# This will:
# 1. Create "textbook_chunks" collection in Qdrant
# 2. Chunk all 17 textbook chapters
# 3. Generate embeddings using Gemini/OpenAI
# 4. Upload chunks with metadata to Qdrant
```

**Expected Output**:
```
Creating Qdrant collection: textbook_chunks
Chunking textbook chapters...
  - Module 1: ROS 2 (4 chapters) -> 250 chunks
  - Module 2: Digital Twin (3 chapters) -> 180 chunks
  - Module 3: NVIDIA Isaac (3 chapters) -> 200 chunks
  - Module 4: VLA (4 chapters) -> 220 chunks
  - Hardware (3 chapters) -> 150 chunks
Total: 1,000 chunks

Generating embeddings...
  - Batch 1/10 (100 chunks) -> Done
  - Batch 2/10 (100 chunks) -> Done
  ...
  - Batch 10/10 (100 chunks) -> Done

Uploading to Qdrant...
  - Uploaded 1,000 chunks successfully

✅ Indexing complete!
```

---

## Running the Application

### 1. Start Backend Server

```bash
cd backend
source venv/bin/activate

# Run with uvicorn
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete
```

**Health Check**:
```bash
curl http://localhost:8001/health
# {"status":"ok","timestamp":"2026-02-22T10:30:00Z"}
```

### 2. Start Frontend Server

```bash
cd textbook

# Run Docusaurus dev server
npm start -- --port 3001 --host 0.0.0.0

# Expected output:
# [SUCCESS] Docusaurus website is running at: http://localhost:3001/
```

### 3. Access Application

- **Textbook**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs (Swagger UI)

---

## Testing the Chatbot

### 1. Manual Testing (Browser)

1. Navigate to http://localhost:3001
2. Log in with existing account (from Phase 2)
3. Click floating "Ask" button (bottom-right)
4. Chat panel slides out from right
5. Type question: "What is VSLAM?"
6. Verify:
   - Typing indicator appears
   - AI response includes explanation
   - Source link is clickable
   - Clicking source navigates to textbook section

### 2. Test Selection Mode

1. Navigate to any textbook chapter
2. Highlight a paragraph
3. Open chat panel
4. Verify "Ask about selection" mode is active
5. Ask: "Can you explain this in simpler terms?"
6. Verify response is focused on selected text

### 3. Test Conversation History

1. Ask several questions
2. Close chat panel
3. Reopen chat panel
4. Verify conversation history is preserved
5. Click "New conversation" button
6. Verify new conversation starts
7. Check conversation sidebar shows both threads

### 4. API Testing (curl)

```bash
# Get JWT token (from Phase 2 login)
TOKEN="your_jwt_token_here"

# Create conversation
curl -X POST http://localhost:8001/api/v1/chat/conversations \
  -H "Authorization: Bearer $TOKEN"

# Send message
CONV_ID="conversation_id_from_above"
curl -X POST http://localhost:8001/api/v1/chat/conversations/$CONV_ID/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is VSLAM?"}'

# Get conversation history
curl -X GET http://localhost:8001/api/v1/chat/conversations/$CONV_ID/messages \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Automated Testing

```bash
# Backend unit tests
cd backend
pytest tests/unit/ -v

# Backend integration tests
pytest tests/integration/ -v

# Frontend tests
cd textbook
npm test

# E2E tests
npm run test:e2e
```

---

## Development Workflow

### 1. TDD Approach (per Constitution)

```bash
# 1. Write test first (RED)
cd backend/tests/unit
# Create test_rag_service.py with failing test

# 2. Run test (should fail)
pytest tests/unit/test_rag_service.py -v

# 3. Implement minimal code (GREEN)
cd backend/src/services
# Implement rag_service.py

# 4. Run test (should pass)
pytest tests/unit/test_rag_service.py -v

# 5. Refactor while keeping tests green
# Improve code quality, add error handling

# 6. Repeat for next feature
```

### 2. Hot Reload

Both servers support hot reload:
- **Backend**: uvicorn `--reload` flag watches Python files
- **Frontend**: Docusaurus watches React/TypeScript files

Changes are reflected immediately without restart.

### 3. Debugging

**Backend**:
```bash
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

**Frontend**:
```bash
# Use browser DevTools
# React DevTools extension recommended
```

---

## Common Issues

### Issue 1: Qdrant Connection Failed

**Symptom**: `ConnectionError: Could not connect to Qdrant`

**Solution**:
1. Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
2. Check Qdrant Cloud dashboard (cluster must be running)
3. Test connection: `curl $QDRANT_URL/collections -H "api-key: $QDRANT_API_KEY"`

### Issue 2: Gemini API Rate Limit

**Symptom**: `429 Too Many Requests` from Gemini API

**Solution**:
1. Switch to OpenAI: Set `LLM_PROVIDER=openai` in `.env`
2. Or wait 1 minute (Gemini free tier: 15 requests/minute)
3. For production, upgrade to Gemini paid tier

### Issue 3: Database Migration Failed

**Symptom**: `relation "conversations" does not exist`

**Solution**:
1. Verify `DATABASE_URL` is correct
2. Run migrations: `alembic upgrade head`
3. Check Neon dashboard (database must be active)

### Issue 4: Chat Panel Not Appearing

**Symptom**: Floating "Ask" button not visible

**Solution**:
1. Verify user is logged in (check localStorage for JWT token)
2. Check browser console for errors
3. Verify `REACT_APP_API_URL` in frontend `.env`
4. Clear browser cache and reload

### Issue 5: Source Links Not Working

**Symptom**: Clicking source link doesn't navigate to chapter

**Solution**:
1. Verify textbook chapters exist at URLs in source references
2. Check URL format: `/docs/module-name/chapter-name#section-id`
3. Verify Docusaurus routing is working (test manual navigation)

---

## Performance Optimization

### Backend
- **Caching**: Implement Redis cache for frequent questions
- **Connection Pooling**: Use asyncpg pool for Postgres
- **Batch Processing**: Batch Qdrant searches when possible

### Frontend
- **Code Splitting**: Lazy load ChatPanel component
- **Memoization**: Use React.memo for message components
- **Virtual Scrolling**: For long conversation histories

---

## Deployment

### Backend (Railway/Render)

```bash
# 1. Create new service on Railway/Render
# 2. Connect GitHub repository
# 3. Set environment variables (same as .env)
# 4. Deploy

# Railway CLI
railway up

# Or Render (auto-deploys on git push)
```

### Frontend (Vercel)

```bash
# 1. Connect GitHub repository to Vercel
# 2. Set environment variables
# 3. Deploy

# Vercel CLI
vercel --prod
```

### Environment Variables (Production)

Update `.env` with production values:
- `DATABASE_URL`: Neon production connection string
- `QDRANT_URL`: Qdrant production cluster
- `CORS_ORIGINS`: Production frontend URL
- `ENVIRONMENT=production`

---

## Monitoring

### Health Checks
- Backend: `GET /health` (returns 200 if healthy)
- Database: Check Neon dashboard for connection count
- Qdrant: Check Qdrant Cloud dashboard for query latency

### Logs
- Backend: uvicorn logs to stdout (captured by Railway/Render)
- Frontend: Vercel function logs in dashboard
- Errors: Check Sentry/LogRocket (if configured)

### Metrics
- Response time: 90% < 5 seconds (per spec)
- Error rate: < 1% (per spec)
- Uptime: 99% target (per spec)

---

## Next Steps

After completing setup:
1. Run `/sp.tasks` to generate implementation task breakdown
2. Follow TDD approach for each task
3. Update `history.md` at end of each session
4. Create ADRs for significant decisions
5. Deploy to production when all tests pass

---

## Support

- **Specification**: See `spec.md` for requirements
- **API Docs**: See `contracts/README.md` for API details
- **Data Model**: See `data-model.md` for database schema
- **Research**: See `research.md` for technical decisions
