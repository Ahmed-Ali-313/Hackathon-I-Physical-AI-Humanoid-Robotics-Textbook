"""
Unit tests for matching_service

Tests:
- is_recommended() exact match logic
- LEVEL_ORDER comparison (none < beginner < intermediate < advanced)
- Hardware OR logic (any match)
- Software AND logic (all must match or exceed)
- Edge cases (null values, empty preferences)
"""

import pytest
from src.services.matching_service import (
    is_recommended,
    LEVEL_ORDER,
    compare_experience_level
)


class TestMatchingService:
    """Test suite for content matching logic"""

    def test_level_order_constant(self):
        """Test that LEVEL_ORDER is correctly defined"""
        assert LEVEL_ORDER == {
            "none": 0,
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }

    def test_compare_experience_level_equal(self):
        """Test comparing equal experience levels"""
        assert compare_experience_level("intermediate", "intermediate") == 0

    def test_compare_experience_level_user_higher(self):
        """Test user level higher than required"""
        assert compare_experience_level("advanced", "beginner") > 0

    def test_compare_experience_level_user_lower(self):
        """Test user level lower than required"""
        assert compare_experience_level("beginner", "advanced") < 0

    def test_compare_experience_level_none_handling(self):
        """Test that 'none' is lowest level"""
        assert compare_experience_level("beginner", "none") > 0
        assert compare_experience_level("none", "beginner") < 0

    def test_is_recommended_exact_hardware_match(self):
        """Test exact hardware match returns True"""
        user_prefs = {
            "workstation_type": "high_end_desktop",
            "edge_kit_available": "jetson_orin",
            "robot_tier_access": "tier_2"
        }
        content_meta = {
            "hardware_tags": ["high_end_desktop", "jetson_orin"],
            "software_requirements": {}
        }

        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_hardware_or_logic(self):
        """Test hardware OR logic - any match is sufficient"""
        user_prefs = {
            "workstation_type": "laptop",
            "edge_kit_available": "jetson_orin"
        }
        content_meta = {
            "hardware_tags": ["high_end_desktop", "jetson_orin"],  # Only jetson_orin matches
            "software_requirements": {}
        }

        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_no_hardware_match(self):
        """Test no hardware match returns False"""
        user_prefs = {
            "workstation_type": "laptop",
            "edge_kit_available": "raspberry_pi"
        }
        content_meta = {
            "hardware_tags": ["high_end_desktop", "jetson_orin"],
            "software_requirements": {}
        }

        assert is_recommended(user_prefs, content_meta) is False

    def test_is_recommended_software_and_logic_all_match(self):
        """Test software AND logic - all requirements must be met"""
        user_prefs = {
            "ros2_level": "advanced",
            "gazebo_level": "intermediate",
            "isaac_level": "beginner"
        }
        content_meta = {
            "hardware_tags": [],
            "software_requirements": {
                "ros2_level": "intermediate",  # User is advanced (meets requirement)
                "gazebo_level": "intermediate",  # Exact match
                "isaac_level": "beginner"  # Exact match
            }
        }

        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_software_and_logic_one_fails(self):
        """Test software AND logic - if one requirement not met, returns False"""
        user_prefs = {
            "ros2_level": "beginner",
            "gazebo_level": "advanced"
        }
        content_meta = {
            "hardware_tags": [],
            "software_requirements": {
                "ros2_level": "intermediate",  # User is beginner (does NOT meet requirement)
                "gazebo_level": "intermediate"  # User is advanced (meets requirement)
            }
        }

        assert is_recommended(user_prefs, content_meta) is False

    def test_is_recommended_user_exceeds_requirement(self):
        """Test that user with higher level meets lower requirement"""
        user_prefs = {
            "ros2_level": "advanced"
        }
        content_meta = {
            "hardware_tags": [],
            "software_requirements": {
                "ros2_level": "beginner"
            }
        }

        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_empty_content_requirements(self):
        """Test content with no requirements matches all users"""
        user_prefs = {
            "workstation_type": "laptop",
            "ros2_level": "beginner"
        }
        content_meta = {
            "hardware_tags": [],
            "software_requirements": {}
        }

        # Content with no requirements should match everyone
        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_null_user_preferences(self):
        """Test user with null preferences"""
        user_prefs = {
            "workstation_type": None,
            "ros2_level": None
        }
        content_meta = {
            "hardware_tags": ["high_end_desktop"],
            "software_requirements": {"ros2_level": "intermediate"}
        }

        assert is_recommended(user_prefs, content_meta) is False

    def test_is_recommended_mixed_hardware_and_software(self):
        """Test combined hardware and software matching"""
        user_prefs = {
            "workstation_type": "high_end_desktop",
            "edge_kit_available": "jetson_orin",
            "ros2_level": "intermediate",
            "isaac_level": "beginner"
        }
        content_meta = {
            "hardware_tags": ["high_end_desktop"],  # Matches
            "software_requirements": {
                "ros2_level": "intermediate",  # Matches
                "isaac_level": "beginner"  # Matches
            }
        }

        assert is_recommended(user_prefs, content_meta) is True

    def test_is_recommended_none_level_handling(self):
        """Test that 'none' level does not meet any requirement"""
        user_prefs = {
            "ros2_level": "none"
        }
        content_meta = {
            "hardware_tags": [],
            "software_requirements": {
                "ros2_level": "beginner"
            }
        }

        assert is_recommended(user_prefs, content_meta) is False
