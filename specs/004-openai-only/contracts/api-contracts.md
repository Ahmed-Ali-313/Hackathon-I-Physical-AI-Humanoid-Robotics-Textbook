# API Contracts: Migrate RAG Chatbot to OpenAI-Only API

**Feature**: 004-openai-only
**Date**: 2026-02-23
**Status**: No Changes Required

## Overview

This migration is an **internal implementation change only**. All REST API endpoints, request/response formats, and client contracts remain unchanged. The frontend and any API consumers are unaffected.

## Unchanged Endpoints

### POST /api/chat/conversations
**Purpose**: Create a new conversation
**Status**: No changes

**Request**:
```json
{
  "title": "string (optional)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

### POST /api/chat/conversations/{conversation_id}/messages
**Purpose**: Send a message and get chatbot response
**Status**: No changes (internal provider switch from Gemini to OpenAI)

**Request**:
```json
{
  "content": "string (max 500 chars)",
  "selected_text": "string (optional, for selection mode)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "assistant",
  "content": "string",
  "sources": [
    {
      "chapter": "string",
      "section": "string",
      "url": "string"
    }
  ],
  "confidence": "float (0.0-1.0)",
  "created_at": "timestamp"
}
```

**Internal Change**: Response is now generated using OpenAI gpt-4o-mini instead of Gemini, but the response format remains identical.

---

### GET /api/chat/conversations/{conversation_id}/messages
**Purpose**: Retrieve conversation history
**Status**: No changes

**Response**:
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user|assistant",
      "content": "string",
      "sources": [...],
      "confidence": "float",
      "created_at": "timestamp"
    }
  ]
}
```

---

### GET /api/chat/conversations
**Purpose**: List user's conversations
**Status**: No changes

**Response**:
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "message_count": "integer"
    }
  ]
}
```

---

### DELETE /api/chat/conversations/{conversation_id}
**Purpose**: Delete a conversation
**Status**: No changes

**Response**:
```json
{
  "success": true
}
```

---

## Internal Service Contracts (Modified)

### EmbeddingService

**Before**:
```python
class EmbeddingService:
    def __init__(self, provider: str = "gemini"):
        # Dual provider support

    async def generate_embedding(self, text: str) -> List[float]:
        # Provider-specific logic
```

**After**:
```python
class EmbeddingService:
    def __init__(self):
        # OpenAI-only, no provider parameter

    async def generate_embedding(self, text: str) -> List[float]:
        # OpenAI-only implementation
```

**Contract Guarantee**: Still returns 768-dimensional float array

---

### AgentService

**Before**:
```python
class AgentService:
    def __init__(self, provider: str = "gemini"):
        # Dual provider support

    async def generate_response(self, query: str, context: List[str]) -> str:
        # Provider-specific logic
```

**After**:
```python
class AgentService:
    def __init__(self):
        # OpenAI-only, no provider parameter

    async def generate_response(self, query: str, context: List[str]) -> str:
        # OpenAI-only implementation
```

**Contract Guarantee**: Still returns string response with same quality and format

---

## Error Responses (Modified)

### New Error Scenarios

**OpenAI API Key Missing**:
```json
{
  "error": "OpenAI API key not configured",
  "status": 500
}
```

**OpenAI Rate Limit**:
```json
{
  "error": "Rate limit exceeded, please try again in 60 seconds",
  "status": 429
}
```

**OpenAI API Unavailable**:
```json
{
  "error": "OpenAI API temporarily unavailable",
  "status": 503
}
```

**Removed Error Scenarios**:
- Gemini API key missing
- Gemini rate limit errors
- Invalid LLM_PROVIDER value

---

## Client Impact Assessment

**Frontend**: ✅ No changes required
- All API endpoints remain the same
- Request/response formats unchanged
- Error handling may see different error messages (OpenAI-specific)

**Mobile Apps**: ✅ No changes required (if applicable)

**Third-party Integrations**: ✅ No changes required

**Testing**: ⚠️ Update integration tests to expect OpenAI-specific behavior
- Remove Gemini provider test cases
- Update error message assertions
- Verify response quality with OpenAI
