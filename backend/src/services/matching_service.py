"""
Matching Service

Business logic for matching content with user preferences.
Implements exact match logic for hardware and software requirements.
"""

from typing import Dict, Any, Optional, List


# Experience level ordering (none < beginner < intermediate < advanced < expert)
LEVEL_ORDER = {
    "none": 0,
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4
}


def compare_experience_level(user_level: str, required_level: str) -> int:
    """
    Compare two experience levels.

    Args:
        user_level: User's experience level
        required_level: Required experience level

    Returns:
        Positive if user_level > required_level
        Zero if user_level == required_level
        Negative if user_level < required_level
    """
    user_order = LEVEL_ORDER.get(user_level, 0)
    required_order = LEVEL_ORDER.get(required_level, 0)
    return user_order - required_order


def is_recommended(
    user_preferences: Dict[str, Any],
    content_metadata: Dict[str, Any]
) -> bool:
    """
    Determine if content is recommended for user based on preferences.

    Matching Logic:
    - Hardware: OR logic - any hardware match is sufficient
    - Software: AND logic - all software requirements must be met or exceeded
    - Empty requirements: Content with no requirements matches all users

    Args:
        user_preferences: User's hardware and software preferences
        content_metadata: Content's hardware_tags and software_requirements

    Returns:
        True if content is recommended, False otherwise
    """
    hardware_tags = content_metadata.get("hardware_tags", []) or []
    software_requirements = content_metadata.get("software_requirements", {}) or {}

    # If content has no requirements, it matches everyone
    if not hardware_tags and not software_requirements:
        return True

    # Hardware matching (OR logic - any match is sufficient)
    hardware_match = False
    if hardware_tags:
        user_hardware = [
            user_preferences.get("workstation_type"),
            user_preferences.get("edge_kit_available"),
            user_preferences.get("robot_tier_access")
        ]

        # Remove None values
        user_hardware = [h for h in user_hardware if h is not None]

        # Check if any user hardware matches any required hardware
        for user_hw in user_hardware:
            if user_hw in hardware_tags:
                hardware_match = True
                break

        # If hardware requirements exist but no match, return False
        if not hardware_match:
            return False

    # Software matching (AND logic - all requirements must be met)
    if software_requirements:
        software_fields = ["ros2_level", "gazebo_level", "unity_level", "isaac_level", "vla_level"]

        for field in software_fields:
            required_level = software_requirements.get(field)

            # Skip if this software is not required
            if required_level is None:
                continue

            user_level = user_preferences.get(field)

            # If user has no level for required software, fail
            if user_level is None:
                return False

            # Compare levels - user must meet or exceed requirement
            if compare_experience_level(user_level, required_level) < 0:
                return False

    return True


def get_recommended_content_ids(
    user_preferences: Dict[str, Any],
    all_content_metadata: List[Dict[str, Any]]
) -> List[str]:
    """
    Get list of recommended content IDs for user.

    Args:
        user_preferences: User's preferences
        all_content_metadata: List of all content metadata

    Returns:
        List of content_ids that match user preferences
    """
    recommended = []

    for content in all_content_metadata:
        if is_recommended(user_preferences, content):
            recommended.append(content["content_id"])

    return recommended
