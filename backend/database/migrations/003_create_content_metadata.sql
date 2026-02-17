-- Migration: 003_create_content_metadata.sql
-- Description: Create content_metadata table with GIN indexes for array and JSONB queries
-- Date: 2026-02-17

-- Create content_metadata table
CREATE TABLE IF NOT EXISTS content_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id VARCHAR(255) UNIQUE NOT NULL,
    content_path VARCHAR(500) NOT NULL,
    title VARCHAR(500) NOT NULL,
    hardware_tags TEXT[],
    software_requirements JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX idx_content_metadata_content_id ON content_metadata(content_id);
CREATE INDEX idx_content_metadata_hardware_tags ON content_metadata USING GIN(hardware_tags);
CREATE INDEX idx_content_metadata_software_requirements ON content_metadata USING GIN(software_requirements);

-- Create trigger for updated_at
CREATE TRIGGER update_content_metadata_updated_at
    BEFORE UPDATE ON content_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE content_metadata IS 'Metadata tags for textbook content sections to enable personalization matching';
COMMENT ON COLUMN content_metadata.content_id IS 'Unique content section identifier (from markdown frontmatter)';
COMMENT ON COLUMN content_metadata.content_path IS 'File path relative to docs/ directory';
COMMENT ON COLUMN content_metadata.title IS 'Content section title';
COMMENT ON COLUMN content_metadata.hardware_tags IS 'Array of required hardware configurations (e.g., ["rtx_12gb", "jetson_orin"])';
COMMENT ON COLUMN content_metadata.software_requirements IS 'JSON object with required software experience levels (e.g., {"ros2_level": "intermediate"})';
