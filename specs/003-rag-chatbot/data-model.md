# Data Model: RAG Chatbot Integration

**Feature**: 003-rag-chatbot
**Date**: 2026-02-22
**Purpose**: Define entities, relationships, and validation rules for chat system

## Entity Relationship Diagram

```
User (from Phase 2)
  ↓ 1:N
Conversation
  ↓ 1:N
ChatMessage
  ↓ 1:N
SourceReference

ChatSession (tracks active sessions)
  ↓ N:1
User
  ↓ N:1
Conversation
```

---

## Entities

### 1. Conversation

**Purpose**: Groups related messages into a conversation thread

**Attributes**:
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (UUID, FK → users.id, NOT NULL): Owner of the conversation
- `title` (VARCHAR(100), NOT NULL): Auto-generated from first question (first 50 chars + "...")
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT NOW()): When conversation started
- `updated_at` (TIMESTAMP, NOT NULL, DEFAULT NOW()): Last modification time
- `last_message_at` (TIMESTAMP, NULLABLE): Timestamp of most recent message
- `message_count` (INTEGER, NOT NULL, DEFAULT 0): Total messages in conversation

**Validation Rules**:
- `title` must be 1-100 characters
- `message_count` must be >= 0
- `message_count` must be <= 500 (per spec constraint)
- `user_id` must reference existing user
- `last_message_at` must be >= `created_at` if not null

**Indexes**:
- Primary: `id`
- Composite: `(user_id, updated_at DESC)` - for fetching user's conversations sorted by recency
- Single: `last_message_at` - for retention policy cleanup

**Lifecycle**:
1. **Created**: When user sends first message (no existing conversation selected)
2. **Updated**: When new message added (update `updated_at`, `last_message_at`, `message_count`)
3. **Deleted**: Automatically after 12 months from `last_message_at` (retention policy)

**Business Rules**:
- Each user can have up to 50 conversation threads (enforced at application level)
- Conversations are private (only accessible by owning user)
- Title is immutable after creation (generated from first question)

---

### 2. ChatMessage

**Purpose**: Represents a single message in a conversation (question or answer)

**Attributes**:
- `id` (UUID, PK): Unique message identifier
- `conversation_id` (UUID, FK → conversations.id ON DELETE CASCADE, NOT NULL): Parent conversation
- `user_id` (UUID, FK → users.id, NOT NULL): User who owns this conversation
- `content` (TEXT, NOT NULL): Message text (question or answer)
- `sender_type` (VARCHAR(10), NOT NULL, CHECK IN ('user', 'ai')): Who sent the message
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT NOW()): When message was created
- `confidence_score` (FLOAT, NULLABLE): RAG confidence (0.0-1.0) for AI messages, NULL for user messages
- `source_references` (JSONB, NULLABLE): Array of source attribution objects (for AI messages)

**Validation Rules**:
- `content` must be 1-2000 characters (user: max 500, AI: max 2000)
- `sender_type` must be 'user' or 'ai'
- `confidence_score` must be 0.0-1.0 if not null
- `confidence_score` must be null for user messages, not null for AI messages
- `source_references` must be valid JSON array if not null
- `conversation_id` must reference existing conversation
- `user_id` must match conversation's user_id

**Indexes**:
- Primary: `id`
- Composite: `(conversation_id, created_at)` - for fetching messages in chronological order
- Single: `user_id` - for user-level queries

**Lifecycle**:
1. **Created**: When user sends message or AI generates response
2. **Immutable**: Messages cannot be edited or deleted individually (only via conversation cascade delete)

**Business Rules**:
- Messages are append-only (no updates or individual deletes)
- User messages always have `sender_type='user'`, `confidence_score=NULL`, `source_references=NULL`
- AI messages always have `sender_type='ai'`, `confidence_score` >= 0.0, `source_references` (may be empty array)
- Each conversation can have up to 500 messages (enforced at application level)

**Source References JSON Schema**:
```json
[
  {
    "chapter_name": "Module 3: NVIDIA Isaac",
    "section_number": "3.2",
    "url": "/docs/module-3-isaac/isaac-sim#section-3-2",
    "relevance_score": 0.85
  }
]
```

---

### 3. SourceReference (Embedded in ChatMessage)

**Purpose**: Links AI responses to specific textbook sections for source attribution

**Note**: This is not a separate table but a structured JSONB field within `ChatMessage.source_references`

**Attributes** (per array element):
- `chapter_name` (STRING, REQUIRED): Human-readable chapter name
- `section_number` (STRING, REQUIRED): Section identifier (e.g., "3.2")
- `url` (STRING, REQUIRED): Relative URL to textbook section
- `relevance_score` (FLOAT, REQUIRED): Qdrant similarity score (0.0-1.0)

**Validation Rules**:
- `chapter_name` must be non-empty string
- `section_number` must match pattern `\d+\.\d+` (e.g., "3.2")
- `url` must start with `/docs/`
- `relevance_score` must be 0.0-1.0
- Array must contain 0-5 elements (top-5 sources max)

**Business Rules**:
- Sources are ordered by `relevance_score` descending
- Only sources with `relevance_score` >= 0.7 are included (per constitution)
- Duplicate URLs are removed (keep highest relevance_score)

---

### 4. ChatSession

**Purpose**: Tracks active chat sessions for managing state and detecting expired sessions

**Attributes**:
- `id` (UUID, PK): Unique session identifier
- `user_id` (UUID, FK → users.id, NOT NULL): User who owns this session
- `conversation_id` (UUID, FK → conversations.id ON DELETE SET NULL, NULLABLE): Currently active conversation
- `started_at` (TIMESTAMP, NOT NULL, DEFAULT NOW()): When session started
- `last_activity_at` (TIMESTAMP, NOT NULL, DEFAULT NOW()): Last user interaction
- `is_active` (BOOLEAN, NOT NULL, DEFAULT TRUE): Whether session is still active

**Validation Rules**:
- `user_id` must reference existing user
- `conversation_id` must reference existing conversation if not null
- `last_activity_at` must be >= `started_at`
- `is_active` must be boolean

**Indexes**:
- Primary: `id`
- Composite: `(user_id, is_active)` - for finding active sessions
- Single: `last_activity_at` - for session expiry cleanup

**Lifecycle**:
1. **Created**: When user opens chat interface
2. **Updated**: On every user interaction (update `last_activity_at`)
3. **Expired**: When `last_activity_at` < NOW() - 30 minutes (mark `is_active=FALSE`)
4. **Deleted**: After 24 hours of inactivity (cleanup job)

**Business Rules**:
- Each user can have only one active session at a time
- Session expires after 30 minutes of inactivity
- Expired sessions trigger re-authentication prompt in UI

---

## Relationships

### User → Conversation (1:N)
- One user can have multiple conversations (up to 50)
- Each conversation belongs to exactly one user
- Cascade: When user deleted, all conversations deleted

### Conversation → ChatMessage (1:N)
- One conversation contains multiple messages (up to 500)
- Each message belongs to exactly one conversation
- Cascade: When conversation deleted, all messages deleted

### User → ChatSession (1:N)
- One user can have multiple sessions (but only one active)
- Each session belongs to exactly one user
- Cascade: When user deleted, all sessions deleted

### ChatSession → Conversation (N:1, Optional)
- Multiple sessions can reference the same conversation
- A session may not have a conversation (new user, no messages yet)
- No cascade: When conversation deleted, session's `conversation_id` set to NULL

---

## State Transitions

### Conversation States
```
[New User] → [First Message] → [Conversation Created]
                                      ↓
                                [Active] ← [New Message Added]
                                      ↓
                                [Inactive] (no messages for 12 months)
                                      ↓
                                [Deleted] (retention policy)
```

### ChatSession States
```
[User Opens Chat] → [Session Created (is_active=TRUE)]
                           ↓
                    [Active] ← [User Interaction]
                           ↓
                    [Expired] (30 min inactivity, is_active=FALSE)
                           ↓
                    [Deleted] (24 hours after expiry)
```

---

## Data Volume Estimates

Based on spec constraints:
- **Users**: 5,000 total
- **Conversations**: 50 per user × 5,000 users = 250,000 max
- **Messages**: 500 per conversation × 250,000 conversations = 125,000,000 max (theoretical)
- **Realistic Messages**: Assume avg 20 messages/conversation = 5,000,000 messages
- **ChatSessions**: ~100 active at any time, ~10,000 total (with cleanup)

**Storage Estimates**:
- Conversation: ~200 bytes × 250,000 = 50 MB
- ChatMessage: ~1 KB × 5,000,000 = 5 GB
- ChatSession: ~150 bytes × 10,000 = 1.5 MB
- **Total**: ~5.05 GB (well within Neon free tier: 10 GB)

---

## Validation Summary

### Application-Level Constraints
- Max 50 conversations per user
- Max 500 messages per conversation
- Max 500 characters per user message
- Max 2000 characters per AI response
- Max 5 source references per AI response
- Session expires after 30 minutes inactivity
- Conversations deleted after 12 months from last message

### Database-Level Constraints
- Foreign key integrity (user_id, conversation_id)
- Check constraints (sender_type, confidence_score range)
- NOT NULL constraints (required fields)
- Unique constraints (none - all entities allow duplicates)
- Cascade deletes (conversation → messages, user → conversations/sessions)

---

## Migration Strategy

### Initial Schema Creation
```sql
-- Run in order:
1. CREATE TABLE conversations (...)
2. CREATE TABLE chat_messages (...)
3. CREATE TABLE chat_sessions (...)
4. CREATE INDEXES
5. CREATE TRIGGERS (update_conversation_stats)
```

### Rollback Plan
```sql
-- Reverse order:
1. DROP TABLE chat_sessions CASCADE
2. DROP TABLE chat_messages CASCADE
3. DROP TABLE conversations CASCADE
```

### Data Seeding
- No seed data required (user-generated content only)
- Test data: Create 3 sample conversations with 10 messages each for E2E tests

---

## Security Considerations

### Row-Level Security (RLS)
- Conversations: User can only access their own conversations
- ChatMessages: User can only access messages from their conversations
- ChatSessions: User can only access their own sessions

### Sensitive Data
- No PII in message content (user responsibility)
- No API keys or secrets in messages (application validation)
- Source references contain only public URLs (no auth tokens)

### Audit Trail
- All messages are immutable (append-only)
- Timestamps track when conversations/messages created
- Retention policy ensures compliance with data minimization
