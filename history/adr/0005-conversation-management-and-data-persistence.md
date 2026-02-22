# ADR-0005: Conversation Management and Data Persistence

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-22
- **Feature:** 003-rag-chatbot
- **Context:** Need to persist conversation history across user sessions, enable conversation navigation, and manage data retention. Must support up to 50 conversations per user with 500 messages each. Clarification established 12-month retention policy and conversation sidebar navigation. Must balance storage costs with user needs for referencing previous conversations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines data persistence and retention strategy
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Redis, AI titles, indefinite retention evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all chat functionality and data management
-->

## Decision

**Storage Strategy:**
- **Database**: Neon Serverless Postgres (structured data, ACID guarantees)
- **Schema**: 3 tables (conversations, chat_messages, chat_sessions)
- **Retention Policy**: 12 months from last message (per clarification)
- **Title Generation**: Auto-generate from first 50 characters of first question (truncate at word boundary + "...")
- **Navigation**: Conversation sidebar in chat panel (list all threads, click to switch)

**Database Schema:**
```sql
-- conversations: Groups messages into threads
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(100) NOT NULL,  -- First 50 chars + "..."
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP,
    message_count INTEGER NOT NULL DEFAULT 0
);

-- chat_messages: Individual messages (user questions, AI responses)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'ai')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_references JSONB  -- Array of {chapter, section, url}
);

-- chat_sessions: Track active sessions for state management
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    conversation_id UUID REFERENCES conversations(id),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

**Retention Policy Implementation:**
- Daily cron job: `DELETE FROM conversations WHERE last_message_at < NOW() - INTERVAL '12 months'`
- Cascade delete removes all associated messages
- User notified 30 days before deletion (future enhancement)

## Consequences

### Positive

- **Persistence**: Postgres ensures reliable storage across sessions (ACID guarantees)
- **Retention Balance**: 12-month policy balances student needs (full course duration) with storage costs
- **Simple Title Generation**: Truncation avoids AI processing overhead (instant, no API costs)
- **Sidebar Navigation**: Standard chat UX pattern (Slack, Discord, ChatGPT) - familiar to users
- **Queryable**: SQL enables complex queries (search conversations, analytics)
- **Cascade Deletes**: Automatic cleanup of messages when conversation deleted
- **JSONB for Sources**: Flexible schema for source references without additional tables
- **Free Tier Sufficient**: Neon free tier (10GB) sufficient for 5,000 users with 5M messages

### Negative

- **Storage Costs**: Postgres storage more expensive than Redis (mitigated by Neon free tier)
- **Retention Management**: Requires cron job for cleanup (operational overhead)
- **Title Truncation**: May cut off mid-word if not careful (mitigated by word boundary detection)
- **No Full-Text Search**: Postgres full-text search not included (would require additional indexes)
- **12-Month Limit**: Students lose access to conversations after 12 months (acceptable tradeoff)
- **No Conversation Merging**: Cannot combine related conversations (acceptable for MVP)

## Alternatives Considered

**Alternative A: AI-Generated Titles**
- **Approach**: Use LLM to generate concise summary of first question as title
- **Why Rejected**: Adds latency (200-300ms per conversation creation), API costs ($0.001 per title), unnecessary complexity, simple truncation sufficient for identification

**Alternative B: Timestamp-Only Titles**
- **Approach**: Title format: "Conversation on Feb 22, 2026 at 3:45 PM"
- **Why Rejected**: Less user-friendly (hard to identify conversations at a glance), doesn't provide context about conversation topic, poor UX for sidebar navigation

**Alternative C: Redis for Chat History**
- **Approach**: Store conversations and messages in Redis (in-memory)
- **Why Rejected**: Postgres provides better durability (Redis requires persistence configuration), SQL querying more powerful than Redis data structures, Neon Postgres free tier sufficient, Redis adds operational complexity

**Alternative D: Indefinite Retention**
- **Approach**: Never delete conversations automatically
- **Why Rejected**: Storage costs grow unbounded, privacy concerns (GDPR compliance), diminishing value after course completion, 12-month policy (per clarification) balances needs

**Alternative E: Conversation Tags/Categories**
- **Approach**: Allow users to tag conversations by topic (ROS 2, Isaac Sim, etc.)
- **Why Rejected**: Out of scope for MVP, adds UI complexity, simple title-based identification sufficient, can be added later based on user feedback

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md) (FR-020 to FR-022)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Research: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 5)
- Data Model: [specs/003-rag-chatbot/data-model.md](../../specs/003-rag-chatbot/data-model.md)
- Clarifications: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md#clarifications) (Q2: 12-month retention, Q3: Sidebar navigation, Q5: Title generation)
- Related ADRs: None
- Official Documentation:
  - [Neon Postgres Documentation](https://neon.tech/docs/introduction)
  - [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
  - [FastAPI with asyncpg](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
