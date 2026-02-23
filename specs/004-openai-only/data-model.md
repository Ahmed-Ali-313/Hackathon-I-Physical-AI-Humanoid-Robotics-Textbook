# Data Model: Migrate RAG Chatbot to OpenAI-Only API

**Feature**: 004-openai-only
**Date**: 2026-02-23
**Status**: Complete

## Overview

This migration **does not introduce new data models or modify existing entities**. All database schemas (Neon Postgres) and vector storage schemas (Qdrant) remain unchanged. The migration only affects:
- Configuration settings (environment variables)
- Service implementation (provider selection logic)

## Existing Entities (Unchanged)

### Conversation
**Purpose**: Represents a chat conversation between user and chatbot
**Storage**: Neon Postgres
**Status**: No changes required

**Key Attributes**:
- id (UUID)
- user_id (UUID, foreign key)
- title (string)
- created_at (timestamp)
- updated_at (timestamp)

### ChatMessage
**Purpose**: Individual messages within a conversation
**Storage**: Neon Postgres
**Status**: No changes required

**Key Attributes**:
- id (UUID)
- conversation_id (UUID, foreign key)
- role (enum: user, assistant, system)
- content (text)
- sources (JSON array of source references)
- confidence (float, 0.0-1.0)
- created_at (timestamp)

### Vector Embedding
**Purpose**: Document chunks with semantic embeddings for RAG retrieval
**Storage**: Qdrant Cloud
**Status**: May require re-indexing if created with Gemini embeddings

**Key Attributes**:
- id (integer or UUID)
- vector (768-dimensional float array)
- payload (metadata):
  - module (string)
  - chapter (string)
  - section (string)
  - content (text)
  - url (string)

**Migration Note**: If existing embeddings were created with Gemini's embedding-001 model, they should be re-indexed using OpenAI text-embedding-3-small for consistency. Check Qdrant collection metadata to determine embedding source.

## Configuration Changes

### Environment Variables (Modified)

**Before (Dual Provider)**:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
LLM_PROVIDER=gemini  # or "openai"
```

**After (OpenAI-Only)**:
```
OPENAI_API_KEY=sk-...
```

**Removed Variables**:
- `GEMINI_API_KEY`: No longer needed
- `LLM_PROVIDER`: No longer needed (OpenAI is implicit)

### Service Configuration (Modified)

**File**: `backend/src/config.py`

**Before**:
```python
class Settings(BaseSettings):
    openai_api_key: str
    gemini_api_key: str
    llm_provider: str = "gemini"  # or "openai"
```

**After**:
```python
class Settings(BaseSettings):
    openai_api_key: str
    # Removed: gemini_api_key, llm_provider
```

## Data Migration Requirements

### Qdrant Vector Embeddings

**Assessment Required**: Determine if existing embeddings were created with Gemini or OpenAI

**If Gemini Embeddings Detected**:
1. Run `backend/scripts/index_textbook.py` with OpenAI configuration
2. Expected duration: ~10-15 minutes for 17 chapters
3. Qdrant collection will be recreated with OpenAI embeddings

**If OpenAI Embeddings Detected**:
- No migration required
- Existing embeddings are compatible

**Verification Command**:
```python
# Check Qdrant collection info
from qdrant_client import QdrantClient
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collection_info = client.get_collection("textbook_embeddings")
print(collection_info.config)  # Check vector size and metadata
```

### Postgres Data

**Status**: No migration required
- Conversation and ChatMessage tables remain unchanged
- Existing chat history is preserved
- No schema changes needed

## Validation

**Post-Migration Checks**:
1. Verify Qdrant embeddings are 768-dimensional
2. Verify chat responses use OpenAI API (check logs)
3. Verify source attribution still works
4. Verify confidence scoring still works (>0.7 threshold)
5. Run full test suite to ensure no regressions
