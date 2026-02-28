-- Migration: 007_add_user_language_preference.sql
-- Feature: 005-urdu-translation
-- Purpose: Extend users table with preferred_language field
-- Date: 2026-02-28

-- Add preferred_language column to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en';

-- Add check constraint for valid language codes
ALTER TABLE users
DROP CONSTRAINT IF EXISTS check_preferred_language;

ALTER TABLE users
ADD CONSTRAINT check_preferred_language
CHECK (preferred_language IN ('en', 'ur'));

-- Add comment for documentation
COMMENT ON COLUMN users.preferred_language IS 'User preferred language for textbook content ("en" for English, "ur" for Urdu)';

-- Update existing users to have default language preference
UPDATE users
SET preferred_language = 'en'
WHERE preferred_language IS NULL;
