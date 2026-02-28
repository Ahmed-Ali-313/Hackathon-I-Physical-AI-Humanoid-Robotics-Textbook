# API Contracts: Urdu Translation

**Feature**: 005-urdu-translation
**Date**: 2026-02-28
**Purpose**: Define API endpoints, request/response schemas, and error codes

## Overview

This document defines the REST API contracts for the Urdu Translation feature, including endpoint specifications, request/response schemas, authentication requirements, and error handling.

**Base URL**: `https://api.example.com/api/v1`

**Authentication**: JWT Bearer token required for all endpoints except health checks

---

## Endpoints

### 1. Translate Chapter

**Endpoint**: `POST /translate`

**Purpose**: Translate a chapter from English to Urdu

**Authentication**: Required (JWT)

**Request**:

```json
{
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "force_refresh": false
}
```

**Request Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chapter_id | string | Yes | Slug-based chapter identifier (e.g., "01-introduction-to-ros2") |
| language_code | string | Yes | Target language code ("ur" only) |
| force_refresh | boolean | No | If true, bypass cache and request fresh translation (default: false) |

**Response** (200 OK):

```json
{
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "translated_content": "# ROS 2 کا تعارف\n\nROS 2 ایک جدید...",
  "cached": true,
  "translated_at": "2026-02-28T10:00:05Z"
}
```

**Response Schema**:

| Field | Type | Description |
|-------|------|-------------|
| chapter_id | string | Chapter identifier |
| language_code | string | Language code |
| translated_content | string | Full translated markdown content |
| cached | boolean | True if served from cache, false if freshly translated |
| translated_at | string | ISO 8601 timestamp of translation |

**Error Responses**:

| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 400 | INVALID_CHAPTER_ID | Invalid chapter identifier format | chapter_id doesn't match pattern |
| 400 | INVALID_LANGUAGE | Unsupported language code | language_code is not "ur" |
| 401 | UNAUTHORIZED | Authentication required | Missing or invalid JWT token |
| 404 | CHAPTER_NOT_FOUND | Chapter not found | chapter_id doesn't exist |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests | User exceeded rate limit (10 req/min) |
| 500 | TRANSLATION_FAILED | Translation service error | OpenAI API error |
| 503 | SERVICE_UNAVAILABLE | Translation service temporarily unavailable | OpenAI API down |

**Example Request**:

```bash
curl -X POST https://api.example.com/api/v1/translate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "chapter_id": "01-introduction-to-ros2",
    "language_code": "ur"
  }'
```

**Example Response**:

```json
{
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "translated_content": "# ROS 2 کا تعارف\n\nROS 2 (Robot Operating System 2) ایک جدید روبوٹکس middleware ہے...",
  "cached": true,
  "translated_at": "2026-02-28T10:00:05Z"
}
```

---

### 2. Get Cached Translation

**Endpoint**: `GET /translate/{chapter_id}`

**Purpose**: Retrieve cached translation if available

**Authentication**: Required (JWT)

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| chapter_id | string | Slug-based chapter identifier |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| language_code | string | No | Target language code (default: "ur") |

**Response** (200 OK):

```json
{
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "translated_content": "# ROS 2 کا تعارف\n\nROS 2 ایک جدید...",
  "cached": true,
  "translated_at": "2026-02-28T10:00:05Z"
}
```

**Error Responses**:

| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 401 | UNAUTHORIZED | Authentication required | Missing or invalid JWT token |
| 404 | TRANSLATION_NOT_FOUND | Translation not found in cache | No cached translation exists |

**Example Request**:

```bash
curl -X GET "https://api.example.com/api/v1/translate/01-introduction-to-ros2?language_code=ur" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 3. Update User Language Preference

**Endpoint**: `PUT /user/preferences`

**Purpose**: Update user's preferred language for all chapters

**Authentication**: Required (JWT)

**Request**:

```json
{
  "preferred_language": "ur"
}
```

**Request Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| preferred_language | string | Yes | Preferred language code ("en" or "ur") |

**Response** (200 OK):

```json
{
  "user_id": "user-123",
  "preferred_language": "ur",
  "updated_at": "2026-02-28T10:00:00Z"
}
```

**Error Responses**:

| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 400 | INVALID_LANGUAGE | Invalid language code | language_code is not "en" or "ur" |
| 401 | UNAUTHORIZED | Authentication required | Missing or invalid JWT token |

**Example Request**:

```bash
curl -X PUT https://api.example.com/api/v1/user/preferences \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "ur"
  }'
```

---

### 4. Get User Language Preference

**Endpoint**: `GET /user/preferences`

**Purpose**: Retrieve user's current language preference

**Authentication**: Required (JWT)

**Response** (200 OK):

```json
{
  "user_id": "user-123",
  "preferred_language": "ur"
}
```

**Error Responses**:

| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 401 | UNAUTHORIZED | Authentication required | Missing or invalid JWT token |

**Example Request**:

```bash
curl -X GET https://api.example.com/api/v1/user/preferences \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 5. Admin: Invalidate Cache

**Endpoint**: `DELETE /admin/cache/{chapter_id}`

**Purpose**: Manually invalidate cached translation for a specific chapter

**Authentication**: Required (JWT with admin role)

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| chapter_id | string | Slug-based chapter identifier, or "all" to invalidate all chapters |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| language_code | string | No | Language code to invalidate (default: "ur") |

**Response** (200 OK):

```json
{
  "invalidated": true,
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "message": "Cache invalidated successfully"
}
```

**Error Responses**:

| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 401 | UNAUTHORIZED | Authentication required | Missing or invalid JWT token |
| 403 | FORBIDDEN | Admin access required | User is not an admin |
| 404 | CACHE_NOT_FOUND | No cache entry found | No cached translation exists |

**Example Request** (single chapter):

```bash
curl -X DELETE "https://api.example.com/api/v1/admin/cache/01-introduction-to-ros2?language_code=ur" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Request** (all chapters):

```bash
curl -X DELETE "https://api.example.com/api/v1/admin/cache/all?language_code=ur" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Error Response Format

All error responses follow this standard format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context if applicable"
    }
  }
}
```

**Example Error Response**:

```json
{
  "error": {
    "code": "INVALID_CHAPTER_ID",
    "message": "Invalid chapter identifier format",
    "details": {
      "chapter_id": "invalid-id",
      "expected_format": "01-chapter-name"
    }
  }
}
```

---

## Rate Limiting

**Limits**:
- Translation requests: 10 per minute per user
- Cache lookups: 100 per minute per user
- Admin operations: 20 per minute per admin

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

**Example**:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1709118000
```

---

## Authentication

**Method**: JWT Bearer token

**Header Format**:

```
Authorization: Bearer <jwt_token>
```

**Token Claims**:

```json
{
  "user_id": "user-123",
  "email": "student@example.com",
  "role": "student",
  "exp": 1709118000
}
```

**Admin Token Claims**:

```json
{
  "user_id": "admin-456",
  "email": "admin@example.com",
  "role": "admin",
  "exp": 1709118000
}
```

---

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: Urdu Translation API
  version: 1.0.0
  description: API for translating textbook chapters to Urdu

servers:
  - url: https://api.example.com/api/v1

security:
  - BearerAuth: []

paths:
  /translate:
    post:
      summary: Translate chapter to Urdu
      tags:
        - Translation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TranslateRequest'
      responses:
        '200':
          description: Translation successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TranslateResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'

  /translate/{chapter_id}:
    get:
      summary: Get cached translation
      tags:
        - Translation
      parameters:
        - name: chapter_id
          in: path
          required: true
          schema:
            type: string
        - name: language_code
          in: query
          schema:
            type: string
            default: ur
      responses:
        '200':
          description: Cached translation found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TranslateResponse'
        '404':
          $ref: '#/components/responses/NotFound'

  /user/preferences:
    get:
      summary: Get user language preference
      tags:
        - User
      responses:
        '200':
          description: User preferences retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserPreference'
    put:
      summary: Update user language preference
      tags:
        - User
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdatePreferenceRequest'
      responses:
        '200':
          description: Preference updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserPreference'

  /admin/cache/{chapter_id}:
    delete:
      summary: Invalidate cached translation (admin only)
      tags:
        - Admin
      parameters:
        - name: chapter_id
          in: path
          required: true
          schema:
            type: string
        - name: language_code
          in: query
          schema:
            type: string
            default: ur
      responses:
        '200':
          description: Cache invalidated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CacheInvalidateResponse'
        '403':
          $ref: '#/components/responses/Forbidden'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    TranslateRequest:
      type: object
      required:
        - chapter_id
        - language_code
      properties:
        chapter_id:
          type: string
          pattern: '^\d{2}-[a-z0-9-]+$'
          example: "01-introduction-to-ros2"
        language_code:
          type: string
          enum: [ur]
          example: "ur"
        force_refresh:
          type: boolean
          default: false

    TranslateResponse:
      type: object
      properties:
        chapter_id:
          type: string
        language_code:
          type: string
        translated_content:
          type: string
        cached:
          type: boolean
        translated_at:
          type: string
          format: date-time

    UserPreference:
      type: object
      properties:
        user_id:
          type: string
        preferred_language:
          type: string
          enum: [en, ur]

    UpdatePreferenceRequest:
      type: object
      required:
        - preferred_language
      properties:
        preferred_language:
          type: string
          enum: [en, ur]

    CacheInvalidateResponse:
      type: object
      properties:
        invalidated:
          type: boolean
        chapter_id:
          type: string
        language_code:
          type: string
        message:
          type: string

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Forbidden:
      description: Forbidden
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    InternalError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

---

## Summary

- **5 endpoints**: Translate, Get cached, Update preference, Get preference, Admin invalidate
- **Authentication**: JWT Bearer token required
- **Rate limiting**: 10 translations/min, 100 cache lookups/min
- **Error handling**: Standard error format with codes and details
- **OpenAPI spec**: Complete specification for API documentation
