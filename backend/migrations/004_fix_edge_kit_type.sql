-- Migration: Fix edge_kit_available column type from boolean to varchar
-- Date: 2026-02-28
-- Issue: Column was boolean but should be string to store values like "jetson_nano", "none", etc.

-- Drop the old check constraint
ALTER TABLE personalization_profiles 
DROP CONSTRAINT IF EXISTS valid_edge_kit;

-- Change column type from boolean to varchar(50)
ALTER TABLE personalization_profiles 
ALTER COLUMN edge_kit_available TYPE VARCHAR(50);

-- Add new check constraint for valid string values
ALTER TABLE personalization_profiles
ADD CONSTRAINT valid_edge_kit 
CHECK (edge_kit_available IS NULL OR edge_kit_available IN ('none', 'jetson_nano', 'jetson_orin', 'raspberry_pi', 'other'));

-- Update any existing boolean values to string equivalents (if any exist)
-- true -> 'jetson_nano', false -> 'none', null -> null
UPDATE personalization_profiles 
SET edge_kit_available = CASE 
    WHEN edge_kit_available::text = 'true' THEN 'jetson_nano'
    WHEN edge_kit_available::text = 'false' THEN 'none'
    ELSE NULL
END
WHERE edge_kit_available IS NOT NULL;
