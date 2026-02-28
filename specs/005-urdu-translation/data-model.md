# Data Model: Urdu Translation

**Feature**: 005-urdu-translation
**Date**: 2026-02-28
**Purpose**: Define entities, relationships, and validation rules for translation feature

## Overview

This document defines the data model for the Urdu Translation feature, including database tables, entity relationships, validation rules, and state transitions.

---

## Entities

### 1. TranslatedChapter

**Purpose**: Cache translated chapter content to minimize API costs and improve performance.

**Table**: `translated_chapters`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| chapter_id | VARCHAR(255) | NOT NULL | Slug-based chapter identifier (e.g., "01-introduction-to-ros2") |
| language_code | VARCHAR(10) | NOT NULL | ISO 639-1 language code ("en", "ur") |
| translated_content | TEXT | NOT NULL | Full translated markdown content |
| original_hash | VARCHAR(64) | NOT NULL | SHA-256 hash of original English content for cache invalidation |
| version | INTEGER | NOT NULL, DEFAULT 1 | Optimistic locking version field |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `UNIQUE(chapter_id, language_code)` - Ensures one translation per chapter per language
- `INDEX idx_chapter_language ON (chapter_id, language_code)` - Fast cache lookups

**Validation Rules**:
- `chapter_id` must match pattern: `^\d{2}-[a-z0-9-]+$` (e.g., "01-introduction-to-ros2")
- `language_code` must be "ur" (only Urdu supported in Phase 4)
- `translated_content` must not be empty
- `original_hash` must be 64-character hex string (SHA-256)
- `version` must be positive integer

**State Transitions**:
1. **Created**: New translation entry created with version=1, translated_content="" (placeholder)
2. **Translated**: Translation completed, translated_content populated, version=2
3. **Stale**: updated_at >30 days old, eligible for refresh
4. **Invalidated**: original_hash doesn't match current content, requires re-translation

**Relationships**:
- No direct foreign key to chapters (chapters are markdown files, not database entities)
- Linked by `chapter_id` slug

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "chapter_id": "01-introduction-to-ros2",
  "language_code": "ur",
  "translated_content": "# ROS 2 کا تعارف\n\nROS 2 ایک جدید...",
  "original_hash": "a3c5f8d2e1b4...",
  "version": 2,
  "created_at": "2026-02-28T10:00:00Z",
  "updated_at": "2026-02-28T10:00:05Z"
}
```

---

### 2. User (Extended)

**Purpose**: Store user authentication and preferences, including language preference.

**Table**: `users` (existing table, extended with new field)

**New Field**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| preferred_language | VARCHAR(10) | DEFAULT 'en' | User's preferred language for textbook content |

**Validation Rules**:
- `preferred_language` must be "en" or "ur"
- Defaults to "en" for existing users

**Migration**:
```sql
ALTER TABLE users
ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';

-- Add check constraint
ALTER TABLE users
ADD CONSTRAINT check_preferred_language
CHECK (preferred_language IN ('en', 'ur'));
```

**Relationships**:
- One user has one preferred language
- Language preference applies to all chapters

**Example**:
```json
{
  "id": "user-123",
  "email": "student@example.com",
  "preferred_language": "ur",
  ...
}
```

---

### 3. Chapter (Conceptual Entity)

**Purpose**: Represents a textbook chapter (markdown file, not a database entity).

**Storage**: Markdown files in `textbook/docs/` directory

**Identifier**: Slug-based (e.g., "01-introduction-to-ros2")

**Attributes** (derived from file):
- `chapter_id`: Filename without extension (e.g., "01-introduction-to-ros2")
- `title`: Extracted from first # header in markdown
- `content`: Full markdown content
- `content_hash`: SHA-256 hash of content (computed on-demand)
- `word_count`: Approximate word count (for chunking decisions)

**Validation Rules**:
- `chapter_id` must match pattern: `^\d{2}-[a-z0-9-]+$`
- Content must be valid markdown
- Must contain at least one # header (title)

**Example**:
```markdown
# Introduction to ROS 2

ROS 2 (Robot Operating System 2) is a modern robotics middleware...

## What is ROS 2?

ROS 2 is the next generation of ROS...
```

---

## Relationships

### TranslatedChapter ↔ Chapter

**Type**: Logical relationship (no foreign key)

**Cardinality**: Many-to-One (many translations per chapter, one chapter per translation)

**Link**: `chapter_id` slug

**Constraints**:
- One translation per (chapter_id, language_code) pair
- Translation can exist without chapter (orphaned cache entries cleaned up periodically)

### User ↔ Language Preference

**Type**: One-to-One (embedded field)

**Cardinality**: One user has one preferred language

**Storage**: `preferred_language` field in `users` table

**Constraints**:
- Preference applies globally to all chapters
- Preference persists across sessions

---

## Database Schema (SQL)

### Create TranslatedChapters Table

```sql
CREATE TABLE translated_chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    translated_content TEXT NOT NULL,
    original_hash VARCHAR(64) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_chapter_language UNIQUE (chapter_id, language_code),
    CONSTRAINT check_language_code CHECK (language_code IN ('ur')),
    CONSTRAINT check_chapter_id_format CHECK (chapter_id ~ '^\d{2}-[a-z0-9-]+$'),
    CONSTRAINT check_original_hash_format CHECK (original_hash ~ '^[a-f0-9]{64}$'),
    CONSTRAINT check_version_positive CHECK (version > 0)
);

CREATE INDEX idx_chapter_language ON translated_chapters(chapter_id, language_code);
CREATE INDEX idx_updated_at ON translated_chapters(updated_at);
```

### Extend Users Table

```sql
ALTER TABLE users
ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';

ALTER TABLE users
ADD CONSTRAINT check_preferred_language
CHECK (preferred_language IN ('en', 'ur'));
```

### Trigger for Updated_At

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_translated_chapters_updated_at
BEFORE UPDATE ON translated_chapters
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## Validation Rules Summary

### TranslatedChapter Validation

```python
from pydantic import BaseModel, Field, validator
import re

class TranslatedChapterCreate(BaseModel):
    chapter_id: str = Field(..., min_length=1, max_length=255)
    language_code: str = Field(..., regex='^ur$')
    translated_content: str = Field(..., min_length=1)
    original_hash: str = Field(..., regex='^[a-f0-9]{64}$')

    @validator('chapter_id')
    def validate_chapter_id_format(cls, v):
        if not re.match(r'^\d{2}-[a-z0-9-]+$', v):
            raise ValueError('chapter_id must match format: 01-chapter-name')
        return v

    @validator('translated_content')
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError('translated_content cannot be empty')
        return v

class TranslatedChapterResponse(BaseModel):
    id: str
    chapter_id: str
    language_code: str
    translated_content: str
    original_hash: str
    version: int
    created_at: str
    updated_at: str
```

### User Preference Validation

```python
class UserPreferenceUpdate(BaseModel):
    preferred_language: str = Field(..., regex='^(en|ur)$')

    @validator('preferred_language')
    def validate_language_code(cls, v):
        if v not in ['en', 'ur']:
            raise ValueError('preferred_language must be "en" or "ur"')
        return v
```

---

## Cache Invalidation Strategy

### Automatic Invalidation

1. **Content Hash Mismatch**:
   - Compute SHA-256 hash of current English chapter content
   - Compare with `original_hash` in cached translation
   - If mismatch, mark cache as stale and request new translation

2. **Time-Based Expiration**:
   - Check `updated_at` timestamp
   - If >30 days old, mark cache as stale
   - Request new translation to incorporate prompt improvements

### Manual Invalidation

1. **Admin API Endpoint**:
   - `DELETE /api/v1/admin/cache/{chapter_id}`
   - Deletes cached translation for specified chapter
   - Forces re-translation on next request

2. **Bulk Invalidation**:
   - `DELETE /api/v1/admin/cache` (all chapters)
   - Useful after major prompt improvements

### Cleanup Strategy

1. **Orphaned Entries**:
   - Periodically check for translations where chapter_id no longer exists
   - Delete orphaned entries (chapter deleted or renamed)

2. **Failed Translations**:
   - Entries with empty `translated_content` and version=1 (placeholder)
   - Delete after 1 hour (indicates failed translation)

---

## Performance Considerations

### Indexes

- `(chapter_id, language_code)` - Primary lookup index for cache hits
- `updated_at` - For finding stale entries during cleanup

### Query Patterns

1. **Cache Lookup** (most frequent):
   ```sql
   SELECT translated_content, original_hash, updated_at
   FROM translated_chapters
   WHERE chapter_id = ? AND language_code = 'ur'
   LIMIT 1;
   ```
   - Uses unique index, O(1) lookup
   - Expected: <10ms

2. **Cache Insert** (rare, first translation):
   ```sql
   INSERT INTO translated_chapters (chapter_id, language_code, translated_content, original_hash, version)
   VALUES (?, 'ur', ?, ?, 1)
   ON CONFLICT (chapter_id, language_code) DO NOTHING;
   ```
   - Uses unique constraint
   - Expected: <50ms

3. **Stale Entry Cleanup** (periodic background job):
   ```sql
   DELETE FROM translated_chapters
   WHERE updated_at < NOW() - INTERVAL '30 days';
   ```
   - Uses updated_at index
   - Expected: <100ms for 100 entries

### Storage Estimates

- Average chapter: 5,000 words = ~30KB markdown
- Translated chapter: ~40KB (Urdu text slightly larger)
- 17 chapters × 40KB = 680KB total
- With metadata: ~1MB total storage

---

## Migration Plan

### Step 1: Create Table

```bash
# Run migration
python backend/scripts/migrate.py 006_add_translation_tables.sql
```

### Step 2: Extend Users Table

```bash
# Run migration
python backend/scripts/migrate.py 007_add_user_language_preference.sql
```

### Step 3: Verify

```bash
# Verify tables created
psql $DATABASE_URL -c "\d translated_chapters"
psql $DATABASE_URL -c "\d users"
```

### Step 4: Seed Data (Optional)

```bash
# Pre-translate popular chapters
python backend/scripts/seed_translations.py --chapters "01-introduction-to-ros2,02-ros2-basics"
```

---

## Summary

- **2 entities**: TranslatedChapter (new), User (extended)
- **1 new table**: `translated_chapters` with optimistic locking
- **1 extended table**: `users` with `preferred_language` field
- **Cache strategy**: Hash-based invalidation + 30-day expiration
- **Performance**: <10ms cache hits, <50ms cache misses
- **Storage**: ~1MB for 17 chapters
