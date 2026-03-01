-- Migration: 008_fix_chapter_id_constraint.sql
-- Feature: 005-urdu-translation
-- Purpose: Fix chapter_id constraint to accept nested paths
-- Date: 2026-03-01

-- Drop the old constraint that only accepts "01-chapter-name" format
ALTER TABLE translated_chapters
DROP CONSTRAINT IF EXISTS check_chapter_id_format;

-- Add new constraint that accepts nested paths like "module-1-ros2/urdf-humanoids"
ALTER TABLE translated_chapters
ADD CONSTRAINT check_chapter_id_format CHECK (chapter_id ~ '^[a-z0-9/_-]+$');

-- Update comment to reflect new format
COMMENT ON COLUMN translated_chapters.chapter_id IS 'Chapter identifier (e.g., "intro", "module-1-ros2/urdf-humanoids")';
