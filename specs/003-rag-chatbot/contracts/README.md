# API Contracts Documentation

**Feature**: RAG Chatbot Integration
**API Version**: 1.0.0
**Base URL**: `/api/v1`

## Overview

The RAG Chatbot API provides endpoints for managing conversations and sending messages to a textbook-grounded AI assistant. All endpoints require JWT authentication (Better-Auth) and return JSON responses.

## Authentication

All endpoints (except `/health`) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

Tokens are obtained from the Better-Auth authentication system (Phase 2).

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/chat/conversations` | List user's conversations | Yes |
| POST | `/chat/conversations` | Create new conversation | Yes |
| GET | `/chat/conversations/{id}` | Get conversation details | Yes |
| DELETE | `/chat/conversations/{id}` | Delete conversation | Yes |
| GET | `/chat/conversations/{id}/messages` | Get conversation messages | Yes |
| POST | `/chat/conversations/{id}/messages` | Send message and get AI response | Yes |
| GET | `/health` | Health check | No |

## Key Features

### RAG Grounding
- All AI responses are grounded in textbook content
- Confidence threshold: 0.7 minimum (per constitution)
- Responses include source attribution with clickable links

### Selection-Based Context
- Users can send `selected_text` parameter for "Ask about selection" mode
- Chatbot answers based only on selected text, not entire textbook
- Still includes source attribution

### Conversation Management
- Up to 50 conversations per user
- Up to 500 messages per conversation
- 12-month retention from last message
- Auto-generated titles from first question

### Error Handling
- User-friendly error messages (no stack traces)
- Specific error codes for different scenarios
- Retry mechanisms for transient failures

## Request/Response Examples

### Send Message (Normal Mode)

**Request:**
```http
POST /api/v1/chat/conversations/123e4567-e89b-12d3-a456-426614174000/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "content": "What is VSLAM?"
}
```

**Response (200 OK):**
```json
{
  "user_message": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user-uuid",
    "content": "What is VSLAM?",
    "sender_type": "user",
    "created_at": "2026-02-22T10:30:00Z",
    "confidence_score": null,
    "source_references": null
  },
  "ai_response": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user-uuid",
    "content": "VSLAM (Visual Simultaneous Localization and Mapping) is a technique that allows robots to build a map of their environment while simultaneously tracking their position within that map using visual sensors like cameras...",
    "sender_type": "ai",
    "created_at": "2026-02-22T10:30:03Z",
    "confidence_score": 0.85,
    "source_references": [
      {
        "chapter_name": "Module 3: NVIDIA Isaac",
        "section_number": "3.2",
        "url": "/docs/module-3-isaac/isaac-sim#section-3-2",
        "relevance_score": 0.85
      }
    ]
  }
}
```

### Send Message (Selection Mode)

**Request:**
```http
POST /api/v1/chat/conversations/123e4567-e89b-12d3-a456-426614174000/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "content": "Can you explain this in simpler terms?",
  "selected_text": "Bipedal locomotion requires dynamic balance control through continuous adjustment of the center of mass relative to the support polygon.",
  "selected_text_metadata": {
    "chapter_name": "Module 4: VLA",
    "section_number": "4.3",
    "url": "/docs/module-4-vla/cognitive-planning#section-4-3"
  }
}
```

**Response (200 OK):**
```json
{
  "user_message": { ... },
  "ai_response": {
    "id": "...",
    "content": "Let me break down bipedal locomotion in simpler terms:\n\n1. **Balance Control**: The robot needs to constantly adjust its balance, similar to how humans shift their weight when standing or walking.\n\n2. **Center of Mass**: This is the point where the robot's weight is concentrated...",
    "sender_type": "ai",
    "confidence_score": 1.0,
    "source_references": [
      {
        "chapter_name": "Module 4: VLA",
        "section_number": "4.3",
        "url": "/docs/module-4-vla/cognitive-planning#section-4-3",
        "relevance_score": 1.0
      }
    ]
  }
}
```

### Uncertainty Response (No Textbook Content Found)

**Request:**
```http
POST /api/v1/chat/conversations/123e4567-e89b-12d3-a456-426614174000/messages
Content-Type: application/json

{
  "content": "What is quantum computing?"
}
```

**Response (200 OK):**
```json
{
  "user_message": { ... },
  "ai_response": {
    "id": "...",
    "content": "I don't have information about this in the textbook. This course focuses on Physical AI and Humanoid Robotics. Related topics covered include:\n- ROS 2 middleware and robot control\n- NVIDIA Isaac Sim for simulation\n- Vision-Language-Action models\n\nWould you like to know more about any of these topics?",
    "sender_type": "ai",
    "confidence_score": 0.0,
    "source_references": []
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Message content exceeds 500 characters",
  "details": {
    "field": "content",
    "max_length": 500,
    "actual_length": 523
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Your session has expired. Please log in again"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Conversation not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many conversations. Maximum 50 conversations per user."
}
```

### 503 Service Unavailable
```json
{
  "error": "service_unavailable",
  "message": "The chatbot is temporarily unavailable. Please try again in a few moments"
}
```

## Rate Limits

- **Conversations**: Max 50 per user
- **Messages**: Max 500 per conversation
- **Message Length**: Max 500 characters (user), max 2000 characters (AI)
- **API Requests**: No explicit rate limit (rely on authentication throttling)

## Data Retention

- Conversations are retained for 12 months from the last message
- After 12 months, conversations and all messages are automatically deleted
- Users can manually delete conversations at any time

## Testing

### Using curl

```bash
# Get conversations
curl -X GET http://localhost:8001/api/v1/chat/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Send message
curl -X POST http://localhost:8001/api/v1/chat/conversations/CONVERSATION_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is VSLAM?"}'
```

### Using Postman

1. Import `chat-api.yaml` into Postman
2. Set environment variable `jwt_token` with your authentication token
3. Run requests from the collection

## OpenAPI Specification

Full OpenAPI 3.0 specification available in `chat-api.yaml`.

To view interactive documentation:
```bash
# Install Swagger UI
npm install -g swagger-ui-watcher

# Serve documentation
swagger-ui-watcher chat-api.yaml
```

## Support

For API issues or questions:
- Check `TROUBLESHOOTING.md` in the backend directory
- Review error messages for specific guidance
- Verify JWT token is valid and not expired
