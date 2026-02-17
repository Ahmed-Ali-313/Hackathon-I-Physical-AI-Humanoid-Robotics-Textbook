-- Migration: 002_create_personalization_profiles.sql
-- Description: Create personalization_profiles table with enums and constraints
-- Date: 2026-02-17

-- Create personalization_profiles table
CREATE TABLE IF NOT EXISTS personalization_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Hardware preferences
    workstation_type VARCHAR(50),
    edge_kit_available VARCHAR(50),
    robot_tier_access VARCHAR(50),

    -- Software experience levels
    ros2_level VARCHAR(50),
    gazebo_level VARCHAR(50),
    unity_level VARCHAR(50),
    isaac_level VARCHAR(50),
    vla_level VARCHAR(50),

    -- Metadata
    is_personalized BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints for enum validation
    CONSTRAINT valid_workstation_type CHECK (
        workstation_type IN ('none', 'standard', 'rtx_12gb', 'rtx_24gb', 'other') OR workstation_type IS NULL
    ),
    CONSTRAINT valid_edge_kit CHECK (
        edge_kit_available IN ('none', 'jetson_orin', 'realsense', 'both', 'other') OR edge_kit_available IS NULL
    ),
    CONSTRAINT valid_robot_tier CHECK (
        robot_tier_access IN ('none', 'quadruped', 'humanoid', 'both', 'other') OR robot_tier_access IS NULL
    ),
    CONSTRAINT valid_experience_level CHECK (
        (ros2_level IN ('none', 'beginner', 'intermediate', 'advanced', 'expert') OR ros2_level IS NULL) AND
        (gazebo_level IN ('none', 'beginner', 'intermediate', 'advanced', 'expert') OR gazebo_level IS NULL) AND
        (unity_level IN ('none', 'beginner', 'intermediate', 'advanced', 'expert') OR unity_level IS NULL) AND
        (isaac_level IN ('none', 'beginner', 'intermediate', 'advanced', 'expert') OR isaac_level IS NULL) AND
        (vla_level IN ('none', 'beginner', 'intermediate', 'advanced', 'expert') OR vla_level IS NULL)
    )
);

-- Create indexes
CREATE INDEX idx_personalization_profiles_user_id ON personalization_profiles(user_id);
CREATE INDEX idx_personalization_profiles_is_personalized ON personalization_profiles(is_personalized);

-- Create trigger for updated_at
CREATE TRIGGER update_personalization_profiles_updated_at
    BEFORE UPDATE ON personalization_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE personalization_profiles IS 'User personalization preferences for content recommendations';
COMMENT ON COLUMN personalization_profiles.user_id IS 'Foreign key to users table (one profile per user)';
COMMENT ON COLUMN personalization_profiles.workstation_type IS 'User workstation configuration (none, standard, rtx_12gb, rtx_24gb, other)';
COMMENT ON COLUMN personalization_profiles.edge_kit_available IS 'Available edge computing hardware (none, jetson_orin, realsense, both, other)';
COMMENT ON COLUMN personalization_profiles.robot_tier_access IS 'Robot hardware access level (none, quadruped, humanoid, both, other)';
COMMENT ON COLUMN personalization_profiles.ros2_level IS 'ROS 2 experience level (none, beginner, intermediate, advanced, expert)';
COMMENT ON COLUMN personalization_profiles.is_personalized IS 'Whether user has completed personalization (false if skipped during signup)';
