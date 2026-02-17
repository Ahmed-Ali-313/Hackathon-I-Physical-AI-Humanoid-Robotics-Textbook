"""
Integration tests for preferences API endpoints

Tests:
- POST /api/v1/preferences (create preferences)
- GET /api/v1/preferences (retrieve preferences)
- Authentication requirements
- Error responses
- Status codes
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestPreferencesAPI:
    """Test suite for preferences API endpoints"""

    def test_create_preferences_success(self, client: TestClient, auth_headers):
        """Test POST /api/v1/preferences with valid data"""
        payload = {
            "workstation_type": "high_end_desktop",
            "edge_kit_available": "jetson_orin",
            "robot_tier_access": "tier_2",
            "ros2_level": "intermediate",
            "gazebo_level": "beginner",
            "unity_level": "none",
            "isaac_level": "beginner",
            "vla_level": "none"
        }

        response = client.post(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["workstation_type"] == "high_end_desktop"
        assert data["ros2_level"] == "intermediate"
        assert data["is_personalized"] is True

    def test_create_preferences_unauthorized(self, client: TestClient):
        """Test POST /api/v1/preferences without authentication"""
        payload = {"workstation_type": "laptop"}

        response = client.post("/api/v1/preferences", json=payload)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_preferences_invalid_enum(self, client: TestClient, auth_headers):
        """Test POST /api/v1/preferences with invalid enum value"""
        payload = {"workstation_type": "invalid_type"}

        response = client.post(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_preferences_duplicate(self, client: TestClient, auth_headers):
        """Test POST /api/v1/preferences when preferences already exist"""
        payload = {"workstation_type": "laptop"}

        # Create first time
        response1 = client.post(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Attempt duplicate
        response2 = client.post(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()

    def test_get_preferences_success(self, client: TestClient, auth_headers_with_profile):
        """Test GET /api/v1/preferences with existing profile"""
        response = client.get(
            "/api/v1/preferences",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        data = response.json()
        assert "workstation_type" in data
        assert "is_personalized" in data

    def test_get_preferences_not_found(self, client: TestClient, auth_headers):
        """Test GET /api/v1/preferences when no profile exists"""
        response = client.get(
            "/api/v1/preferences",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_preferences_unauthorized(self, client: TestClient):
        """Test GET /api/v1/preferences without authentication"""
        response = client.get("/api/v1/preferences")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_preferences_response_schema(self, client: TestClient, auth_headers_with_profile):
        """Test that response matches expected schema"""
        response = client.get(
            "/api/v1/preferences",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields present
        expected_fields = [
            "id", "user_id", "workstation_type", "edge_kit_available",
            "robot_tier_access", "ros2_level", "gazebo_level",
            "unity_level", "isaac_level", "vla_level",
            "is_personalized", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
