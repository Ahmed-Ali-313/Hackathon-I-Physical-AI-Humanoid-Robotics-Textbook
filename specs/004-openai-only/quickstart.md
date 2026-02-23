# Quickstart: Migrate RAG Chatbot to OpenAI-Only API

**Feature**: 004-openai-only
**Date**: 2026-02-23
**Audience**: Developers implementing this migration

## Prerequisites

- Python 3.11+ installed
- Access to OpenAI API (API key)
- Existing RAG chatbot codebase on branch `003-rag-chatbot`
- Qdrant Cloud instance (existing)
- Neon Postgres instance (existing)

## Migration Steps

### Step 1: Update Environment Variables

**File**: `backend/.env`

**Remove these variables**:
```bash
GEMINI_API_KEY=AIza...
LLM_PROVIDER=gemini
```

**Keep only**:
```bash
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
DATABASE_URL=postgresql://...
```

### Step 2: Update Dependencies

**File**: `backend/requirements.txt`

**Remove**:
```
google-generativeai==0.3.2
```

**Keep** (verify these are present):
```
openai>=1.0.0
qdrant-client>=1.7.0
fastapi>=0.104.0
pydantic>=2.0.0
```

**Install updated dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Update Configuration

**File**: `backend/src/config.py`

**Before**:
```python
class Settings(BaseSettings):
    openai_api_key: str
    gemini_api_key: str
    llm_provider: str = "gemini"
```

**After**:
```python
class Settings(BaseSettings):
    openai_api_key: str
    # Removed: gemini_api_key, llm_provider
```

### Step 4: Refactor Embedding Service

**File**: `backend/src/services/embedding_service.py`

**Changes**:
1. Remove `import google.generativeai as genai`
2. Remove `provider` parameter from `__init__`
3. Remove Gemini-specific methods (`_generate_gemini_embedding`)
4. Keep only OpenAI implementation
5. Update model to `text-embedding-3-small`

**Expected result**: Single, simple embedding service using OpenAI only

### Step 5: Refactor Agent Service

**File**: `backend/src/services/agent_service.py`

**Changes**:
1. Remove Gemini imports
2. Remove `provider` parameter from `__init__`
3. Remove Gemini-specific methods
4. Keep only OpenAI implementation
5. Update model to `gpt-4o-mini`

### Step 6: Update Indexing Script

**File**: `backend/scripts/index_textbook.py`

**Changes**:
1. Remove Gemini embedding generation logic
2. Use OpenAI embeddings only
3. Update rate limiting if needed

### Step 7: Check Vector Embeddings

**Verify existing embeddings**:
```bash
cd backend
python -c "
from qdrant_client import QdrantClient
import os
client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
info = client.get_collection('textbook_embeddings')
print(f'Vector size: {info.config.params.vectors.size}')
print(f'Point count: {info.points_count}')
"
```

**If vector size is 768 and embeddings were created with OpenAI**: ✅ No re-indexing needed

**If embeddings were created with Gemini**: ⚠️ Re-index required
```bash
cd backend
python scripts/index_textbook.py
```

### Step 8: Update Tests

**Files to modify**:
- `backend/tests/unit/test_embedding_service.py`
- `backend/tests/unit/test_agent_service.py`
- `backend/tests/unit/test_config.py`
- `backend/tests/integration/test_chat_flow.py`

**Changes**:
1. Remove Gemini provider test cases
2. Remove tests for `LLM_PROVIDER` configuration
3. Update mocks to use OpenAI only
4. Update error message assertions

**Run tests**:
```bash
cd backend
pytest tests/ -v
```

### Step 9: Update Documentation

**Files to modify**:
- `README.md`: Update setup instructions
- `.specify/memory/constitution.md`: Update to v3.0.0, remove dual API requirement
- `.env.example`: Remove Gemini variables

### Step 10: Verify Functionality

**Start backend**:
```bash
cd backend
./venv/bin/python -m uvicorn src.main:app --reload --port 8001
```

**Test chat endpoint**:
```bash
curl -X POST http://localhost:8001/api/chat/conversations/test-id/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is VSLAM?"}'
```

**Expected**: Response generated using OpenAI with sources and confidence score

## Rollback Plan

If migration fails:

1. **Restore environment variables**:
   ```bash
   GEMINI_API_KEY=AIza...
   LLM_PROVIDER=gemini
   ```

2. **Revert code changes**:
   ```bash
   git checkout 003-rag-chatbot
   ```

3. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Success Criteria

- ✅ Backend starts without errors with only `OPENAI_API_KEY` configured
- ✅ Chat queries return responses using OpenAI API
- ✅ Source attribution still works
- ✅ Confidence scoring still works (>0.7 threshold)
- ✅ All tests pass
- ✅ No Gemini references in codebase (`grep -r "gemini" backend/src/`)
- ✅ Documentation reflects OpenAI-only setup

## Troubleshooting

**Error: "OpenAI API key not configured"**
- Check `.env` file has `OPENAI_API_KEY=sk-...`
- Verify environment variables are loaded

**Error: "Rate limit exceeded"**
- OpenAI free tier has rate limits
- Wait 60 seconds and retry
- Consider upgrading OpenAI plan

**Error: "Embedding dimension mismatch"**
- Qdrant may have Gemini embeddings (different dimensions)
- Re-run `python scripts/index_textbook.py`

## Estimated Time

- Code changes: 2-3 hours
- Testing: 1-2 hours
- Re-indexing (if needed): 10-15 minutes
- Documentation: 30 minutes

**Total**: 4-6 hours
