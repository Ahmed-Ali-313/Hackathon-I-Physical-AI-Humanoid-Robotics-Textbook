# Data Model: User Personalization System

**Feature**: 002-personalization
**Date**: 2026-02-17
**Status**: Phase 1 Complete

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the user personalization system.

---

## Entity Definitions

### 1. User

**Purpose**: Represents an authenticated user account (managed by Better-Auth).

**Attributes**:
- `id` (UUID, primary key): Unique user identifier
- `email` (string, unique, required): User's email address
- `password_hash` (string, required): Hashed password (Better-Auth managed)
- `created_at` (timestamp, required): Account creation timestamp
- `updated_at` (timestamp, required): Last update timestamp

**Relationships**:
- One-to-one with PersonalizationProfile
- One-to-many with PreferenceHistory

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique across all users
- Password must meet Better-Auth requirements (handled by auth system)

**Notes**:
- This entity is primarily managed by Better-Auth
- We only reference user.id for personalization associations

---

### 2. PersonalizationProfile

**Purpose**: Stores user's hardware and software preferences collected during signup.

**Attributes**:
- `id` (UUID, primary key): Unique profile identifier
- `user_id` (UUID, foreign key → User.id, unique, required): Associated user
- `workstation_type` (enum, nullable): User's workstation configuration
- `edge_kit_available` (enum, nullable): Available edge computing hardware
- `robot_tier_access` (enum, nullable): Robot hardware access level
- `ros2_level` (enum, nullable): ROS 2 experience level
- `gazebo_level` (enum, nullable): Gazebo experience level
- `unity_level` (enum, nullable): Unity experience level
- `isaac_level` (enum, nullable): NVIDIA Isaac experience level
- `vla_level` (enum, nullable): VLA experience level
- `is_personalized` (boolean, required, default=false): Whether user completed personalization
- `created_at` (timestamp, required): Profile creation timestamp
- `updated_at` (timestamp, required): Last update timestamp

**Enum Values**:

**workstation_type**:
- `none` - No workstation
- `standard` - Standard workstation (no GPU)
- `rtx_12gb` - Workstation with RTX GPU (12GB+ VRAM)
- `rtx_24gb` - Workstation with RTX GPU (24GB+ VRAM)
- `other` - Other configuration

**edge_kit_available**:
- `none` - No edge kit
- `jetson_orin` - NVIDIA Jetson Orin Nano
- `realsense` - Intel RealSense camera
- `both` - Both Jetson and RealSense
- `other` - Other edge kit

**robot_tier_access**:
- `none` - No robot hardware
- `quadruped` - Quadruped (e.g., Unitree Go2)
- `humanoid` - Humanoid (e.g., Unitree G1)
- `both` - Both quadruped and humanoid
- `other` - Other robot hardware

**Experience Levels** (ros2_level, gazebo_level, unity_level, isaac_level, vla_level):
- `none` - No experience
- `beginner` - Beginner level
- `intermediate` - Intermediate level
- `advanced` - Advanced level
- `expert` - Expert level

**Relationships**:
- Many-to-one with User (user_id foreign key)
- One-to-many with PreferenceHistory

**Validation Rules**:
- All enum fields must be from predefined values or null
- At least one preference field should be non-null if is_personalized=true
- user_id must reference existing User.id
- user_id must be unique (one profile per user)

**State Transitions**:
1. **Created (not personalized)**: is_personalized=false, all preference fields null
2. **Personalized**: is_personalized=true, at least one preference field set
3. **Updated**: Any preference field changed, updated_at timestamp refreshed

**Indexes**:
- Primary key on id
- Unique index on user_id
- Index on is_personalized (for querying non-personalized users)

---

### 3. ContentMetadata

**Purpose**: Stores personalization tags for textbook content sections to enable preference matching.

**Attributes**:
- `id` (UUID, primary key): Unique metadata identifier
- `content_id` (string, unique, required): Content section identifier (from frontmatter)
- `content_path` (string, required): File path relative to docs/ directory
- `title` (string, required): Content section title
- `hardware_tags` (array of enum, nullable): Required hardware configurations
- `software_requirements` (JSON, nullable): Required software experience levels
- `created_at` (timestamp, required): Metadata creation timestamp
- `updated_at` (timestamp, required): Last sync timestamp

**hardware_tags Array Values**:
- Same enum values as PersonalizationProfile.workstation_type, edge_kit_available, robot_tier_access
- Example: `["rtx_12gb", "jetson_orin"]`

**software_requirements JSON Structure**:
```json
{
  "ros2_level": "intermediate",
  "isaac_level": "beginner"
}
```

**Relationships**:
- None (standalone entity, matched at query time)

**Validation Rules**:
- content_id must be unique
- content_path must be valid relative path
- hardware_tags array elements must be valid enum values
- software_requirements keys must be valid tool names (ros2_level, gazebo_level, etc.)
- software_requirements values must be valid experience levels

**Indexes**:
- Primary key on id
- Unique index on content_id
- GIN index on hardware_tags (for array containment queries)
- GIN index on software_requirements (for JSON queries)

**Notes**:
- Populated by build-time sync script from Markdown frontmatter
- Updated on every build to stay in sync with content

---

### 4. PreferenceHistory

**Purpose**: Audit log of all preference changes for compliance and debugging.

**Attributes**:
- `id` (UUID, primary key): Unique history entry identifier
- `user_id` (UUID, foreign key → User.id, required): User who made the change
- `profile_id` (UUID, foreign key → PersonalizationProfile.id, required): Affected profile
- `field_name` (string, required): Name of changed field
- `old_value` (string, nullable): Previous value (null for initial creation)
- `new_value` (string, nullable): New value (null for deletion)
- `changed_at` (timestamp, required): When change occurred
- `change_source` (enum, required): How change was made

**change_source Enum Values**:
- `signup` - Initial preference collection during signup
- `profile_update` - User updated preferences from profile settings
- `admin` - Admin-initiated change (future use)
- `system` - System-initiated change (e.g., migration)

**Relationships**:
- Many-to-one with User (user_id foreign key)
- Many-to-one with PersonalizationProfile (profile_id foreign key)

**Validation Rules**:
- user_id must reference existing User.id
- profile_id must reference existing PersonalizationProfile.id
- field_name must be valid PersonalizationProfile field
- At least one of old_value or new_value must be non-null

**Indexes**:
- Primary key on id
- Index on user_id (for user audit queries)
- Index on profile_id (for profile history queries)
- Index on changed_at (for time-based queries)

**Retention Policy**:
- Keep all history records indefinitely for audit compliance
- Consider archiving records older than 2 years to separate table (future optimization)

---

## Entity Relationship Diagram

```text
┌─────────────────┐
│      User       │
│  (Better-Auth)  │
└────────┬────────┘
         │ 1
         │
         │ 1
┌────────▼────────────────────┐
│  PersonalizationProfile     │
│  - workstation_type         │
│  - edge_kit_available       │
│  - robot_tier_access        │
│  - ros2_level               │
│  - gazebo_level             │
│  - unity_level              │
│  - isaac_level              │
│  - vla_level                │
│  - is_personalized          │
└────────┬────────────────────┘
         │ 1
         │
         │ *
┌────────▼────────────────────┐
│   PreferenceHistory         │
│  - field_name               │
│  - old_value                │
│  - new_value                │
│  - changed_at               │
│  - change_source            │
└─────────────────────────────┘

┌─────────────────────────────┐
│    ContentMetadata          │
│  (standalone, no FK)        │
│  - content_id               │
│  - hardware_tags[]          │
│  - software_requirements{}  │
└─────────────────────────────┘
```

---

## Database Schema (PostgreSQL)

```sql
-- Users table (managed by Better-Auth, shown for reference)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Personalization profiles
CREATE TABLE personalization_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workstation_type VARCHAR(50),
    edge_kit_available VARCHAR(50),
    robot_tier_access VARCHAR(50),
    ros2_level VARCHAR(50),
    gazebo_level VARCHAR(50),
    unity_level VARCHAR(50),
    isaac_level VARCHAR(50),
    vla_level VARCHAR(50),
    is_personalized BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

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

CREATE INDEX idx_personalization_is_personalized ON personalization_profiles(is_personalized);

-- Content metadata
CREATE TABLE content_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id VARCHAR(255) UNIQUE NOT NULL,
    content_path VARCHAR(500) NOT NULL,
    title VARCHAR(500) NOT NULL,
    hardware_tags TEXT[],
    software_requirements JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_content_metadata_content_id ON content_metadata(content_id);
CREATE INDEX idx_content_metadata_hardware_tags ON content_metadata USING GIN(hardware_tags);
CREATE INDEX idx_content_metadata_software_requirements ON content_metadata USING GIN(software_requirements);

-- Preference history (audit log)
CREATE TABLE preference_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES personalization_profiles(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    change_source VARCHAR(50) NOT NULL,

    CONSTRAINT valid_change_source CHECK (
        change_source IN ('signup', 'profile_update', 'admin', 'system')
    ),
    CONSTRAINT has_value CHECK (
        old_value IS NOT NULL OR new_value IS NOT NULL
    )
);

CREATE INDEX idx_preference_history_user_id ON preference_history(user_id);
CREATE INDEX idx_preference_history_profile_id ON preference_history(profile_id);
CREATE INDEX idx_preference_history_changed_at ON preference_history(changed_at);
```

---

## Data Access Patterns

### Pattern 1: Fetch User Preferences (Most Common)
```sql
SELECT * FROM personalization_profiles WHERE user_id = $1;
```
**Frequency**: Every authenticated page load
**Performance**: <10ms (indexed on user_id)
**Caching**: 5-minute TTL in-memory cache

### Pattern 2: Match Content to Preferences
```sql
SELECT cm.* FROM content_metadata cm
WHERE
    -- Hardware match (OR logic within array)
    (cm.hardware_tags && ARRAY[$1, $2, $3]::TEXT[] OR cm.hardware_tags IS NULL)
    AND
    -- Software match (level >= required)
    (
        (cm.software_requirements->>'ros2_level' IS NULL OR
         level_order(cm.software_requirements->>'ros2_level') <= level_order($4))
        AND
        (cm.software_requirements->>'isaac_level' IS NULL OR
         level_order(cm.software_requirements->>'isaac_level') <= level_order($5))
        -- ... repeat for other tools
    );
```
**Frequency**: Once per session (cached in frontend)
**Performance**: <50ms (GIN indexes on arrays and JSONB)

### Pattern 3: Update Preferences
```sql
BEGIN;
UPDATE personalization_profiles
SET workstation_type = $1, updated_at = NOW()
WHERE user_id = $2;

INSERT INTO preference_history (user_id, profile_id, field_name, old_value, new_value, change_source)
VALUES ($2, $3, 'workstation_type', $4, $1, 'profile_update');
COMMIT;
```
**Frequency**: Rare (user-initiated updates)
**Performance**: <20ms (transactional, indexed)

### Pattern 4: Audit Query
```sql
SELECT * FROM preference_history
WHERE user_id = $1
ORDER BY changed_at DESC
LIMIT 50;
```
**Frequency**: Very rare (admin/support queries)
**Performance**: <30ms (indexed on user_id and changed_at)

---

## Migration Strategy

**Order of Execution**:
1. Create users table (if not exists from Better-Auth)
2. Create personalization_profiles table
3. Create content_metadata table
4. Create preference_history table

**Rollback Plan**:
- Drop tables in reverse order (preference_history → content_metadata → personalization_profiles)
- Foreign key constraints ensure referential integrity

**Data Seeding**:
- No seed data required for production
- Test fixtures should include sample users, profiles, and content metadata

---

## Summary

**Total Entities**: 4 (User, PersonalizationProfile, ContentMetadata, PreferenceHistory)
**Total Relationships**: 3 foreign key relationships
**Indexes**: 9 indexes for query optimization
**Constraints**: 6 check constraints for data integrity
**Estimated Storage**: ~1KB per user profile, ~500 bytes per content metadata entry, ~200 bytes per history entry
