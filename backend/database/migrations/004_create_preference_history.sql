-- Migration: 004_create_preference_history.sql
-- Description: Create preference_history audit log table
-- Date: 2026-02-17

-- Create preference_history table
CREATE TABLE IF NOT EXISTS preference_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES personalization_profiles(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    change_source VARCHAR(50) NOT NULL,

    -- Constraints
    CONSTRAINT valid_change_source CHECK (
        change_source IN ('signup', 'profile_update', 'admin', 'system')
    ),
    CONSTRAINT has_value CHECK (
        old_value IS NOT NULL OR new_value IS NOT NULL
    )
);

-- Create indexes for audit queries
CREATE INDEX idx_preference_history_user_id ON preference_history(user_id);
CREATE INDEX idx_preference_history_profile_id ON preference_history(profile_id);
CREATE INDEX idx_preference_history_changed_at ON preference_history(changed_at);

-- Add comments
COMMENT ON TABLE preference_history IS 'Audit log of all preference changes for compliance and debugging';
COMMENT ON COLUMN preference_history.user_id IS 'User who made the change';
COMMENT ON COLUMN preference_history.profile_id IS 'Affected personalization profile';
COMMENT ON COLUMN preference_history.field_name IS 'Name of changed field (e.g., "workstation_type", "ros2_level")';
COMMENT ON COLUMN preference_history.old_value IS 'Previous value (null for initial creation)';
COMMENT ON COLUMN preference_history.new_value IS 'New value (null for deletion)';
COMMENT ON COLUMN preference_history.changed_at IS 'Timestamp when change occurred';
COMMENT ON COLUMN preference_history.change_source IS 'How change was made (signup, profile_update, admin, system)';
