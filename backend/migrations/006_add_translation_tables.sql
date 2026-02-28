-- Migration: 006_add_translation_tables.sql
-- Feature: 005-urdu-translation
-- Purpose: Create translated_chapters table for caching translated content
-- Date: 2026-02-28

-- Create translated_chapters table
CREATE TABLE IF NOT EXISTS translated_chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    translated_content TEXT NOT NULL,
    original_hash VARCHAR(64) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_chapter_language UNIQUE (chapter_id, language_code),
    CONSTRAINT check_language_code CHECK (language_code IN ('ur')),
    CONSTRAINT check_chapter_id_format CHECK (chapter_id ~ '^\d{2}-[a-z0-9-]+$'),
    CONSTRAINT check_original_hash_format CHECK (original_hash ~ '^[a-f0-9]{64}$'),
    CONSTRAINT check_version_positive CHECK (version > 0)
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_chapter_language ON translated_chapters(chapter_id, language_code);
CREATE INDEX IF NOT EXISTS idx_updated_at ON translated_chapters(updated_at);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_translated_chapters_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS update_translated_chapters_updated_at_trigger ON translated_chapters;
CREATE TRIGGER update_translated_chapters_updated_at_trigger
BEFORE UPDATE ON translated_chapters
FOR EACH ROW
EXECUTE FUNCTION update_translated_chapters_updated_at();

-- Add comment for documentation
COMMENT ON TABLE translated_chapters IS 'Cache for translated textbook chapters with optimistic locking';
COMMENT ON COLUMN translated_chapters.chapter_id IS 'Slug-based chapter identifier (e.g., "01-introduction-to-ros2")';
COMMENT ON COLUMN translated_chapters.language_code IS 'ISO 639-1 language code ("ur" for Urdu)';
COMMENT ON COLUMN translated_chapters.original_hash IS 'SHA-256 hash of original English content for cache invalidation';
COMMENT ON COLUMN translated_chapters.version IS 'Optimistic locking version field';
