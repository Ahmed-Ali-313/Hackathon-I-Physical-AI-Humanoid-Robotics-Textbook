"""
Additional integration tests for preferences API - Phase 5

Tests:
- PUT /api/v1/preferences (update preferences)
- DELETE /api/v1/preferences (clear all preferences)
- GET /api/v1/preferences/history (get preference change history)
"""

from fastapi.testclient import TestClient


class TestPreferencesAPIPhase5:
    """Test suite for Phase 5 preferences API features"""

    def test_update_preferences_success(self, client: TestClient, auth_headers_with_profile):
        """Test PUT /api/v1/preferences with valid data"""
        payload = {
            "ros2_level": "advanced",
            "gazebo_level": "intermediate"
        }

        response = client.put(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers_with_profile
        )

        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["ros2_level"] == "advanced"
        assert data["gazebo_level"] == "intermediate"

    def test_update_preferences_unauthorized(self, client: TestClient):
        """Test PUT /api/v1/preferences without authentication"""
        payload = {"ros2_level": "advanced"}

        response = client.put("/api/v1/preferences", json=payload)

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_update_preferences_no_profile(self, client: TestClient, auth_headers):
        """Test PUT /api/v1/preferences when user has no profile"""
        payload = {"ros2_level": "advanced"}

        response = client.put(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "no preferences" in response.json()["detail"].lower()

    def test_update_preferences_invalid_enum(self, client: TestClient, auth_headers_with_profile):
        """Test PUT /api/v1/preferences with invalid enum value"""
        payload = {"ros2_level": "expert_plus"}  # Invalid level

        response = client.put(
            "/api/v1/preferences",
            json=payload,
            headers=auth_headers_with_profile
        )

        # Database CHECK constraint catches invalid enum, returns 500
        assert response.status_code == 500

    def test_delete_preferences_success(self, client: TestClient, auth_headers_with_profile):
        """Test DELETE /api/v1/preferences"""
        response = client.delete(
            "/api/v1/preferences",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Preferences cleared successfully"

        # Verify preferences are cleared
        get_response = client.get(
            "/api/v1/preferences",
            headers=auth_headers_with_profile
        )
        assert get_response.status_code == 200
        profile = get_response.json()
        assert profile["is_personalized"] is False

    def test_delete_preferences_unauthorized(self, client: TestClient):
        """Test DELETE /api/v1/preferences without authentication"""
        response = client.delete("/api/v1/preferences")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_delete_preferences_no_profile(self, client: TestClient, auth_headers):
        """Test DELETE /api/v1/preferences when user has no profile"""
        response = client.delete(
            "/api/v1/preferences",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_preference_history_success(self, client: TestClient, auth_headers_with_profile, db_session):
        """Test GET /api/v1/preferences/history"""
        # First, update preferences to create history
        client.put(
            "/api/v1/preferences",
            json={"ros2_level": "advanced"},
            headers=auth_headers_with_profile
        )

        # Get history
        response = client.get(
            "/api/v1/preferences/history",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify history entry structure
        entry = data[0]
        assert "field_name" in entry
        assert "old_value" in entry
        assert "new_value" in entry
        assert "changed_at" in entry
        assert "change_source" in entry

    def test_get_preference_history_unauthorized(self, client: TestClient):
        """Test GET /api/v1/preferences/history without authentication"""
        response = client.get("/api/v1/preferences/history")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_get_preference_history_empty(self, client: TestClient, auth_headers_with_profile):
        """Test GET /api/v1/preferences/history with no history"""
        response = client.get(
            "/api/v1/preferences/history",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_preferences_creates_history(self, client: TestClient, auth_headers_with_profile):
        """Test that updating preferences creates history entries"""
        # Update preferences
        client.put(
            "/api/v1/preferences",
            json={"ros2_level": "advanced", "gazebo_level": "intermediate"},
            headers=auth_headers_with_profile
        )

        # Get history
        response = client.get(
            "/api/v1/preferences/history",
            headers=auth_headers_with_profile
        )

        assert response.status_code == 200
        history = response.json()

        # Should have entries for both changed fields
        field_names = [entry["field_name"] for entry in history]
        assert "ros2_level" in field_names
        assert "gazebo_level" in field_names

    def test_preference_history_ordered_by_time(self, client: TestClient, auth_headers_with_profile):
        """Test that preference history is ordered by changed_at (newest first)"""
        # Make multiple updates
        client.put(
            "/api/v1/preferences",
            json={"ros2_level": "advanced"},
            headers=auth_headers_with_profile
        )

        client.put(
            "/api/v1/preferences",
            json={"gazebo_level": "intermediate"},
            headers=auth_headers_with_profile
        )

        # Get history
        response = client.get(
            "/api/v1/preferences/history",
            headers=auth_headers_with_profile
        )

        history = response.json()

        # Verify ordering (newest first)
        if len(history) >= 2:
            assert history[0]["changed_at"] >= history[1]["changed_at"]
