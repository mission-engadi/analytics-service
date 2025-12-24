"""Integration tests for goal endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


class TestGoalEndpoints:
    """Test goal tracking and management."""

    @pytest.mark.asyncio
    async def test_create_goal(self, async_client: AsyncClient, auth_headers: dict):
        """Test goal creation."""
        data = {
            "name": "Q4 Donation Goal",
            "description": "Reach $100,000 in donations",
            "metric_type": "donation",
            "target_value": 100000.0,
            "current_value": 25000.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "alert_threshold": 0.75,
            "created_by": "test-user-123"
        }
        response = await async_client.post("/api/v1/goals", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert result["metric_type"] == "donation"
        assert result["target_value"] == 100000.0
        assert result["status"] == "active"
        assert "progress_percentage" in result

    @pytest.mark.asyncio
    async def test_get_goal(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieving a goal."""
        # Create goal first
        create_data = {
            "name": "Partner Acquisition Goal",
            "metric_type": "partner",
            "target_value": 50.0,
            "current_value": 10.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=180)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]

        # Get goal
        response = await async_client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == goal_id
        assert result["name"] == "Partner Acquisition Goal"

    @pytest.mark.asyncio
    async def test_update_goal(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating a goal."""
        # Create goal first
        create_data = {
            "name": "Update Test Goal",
            "metric_type": "project",
            "target_value": 20.0,
            "current_value": 5.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]

        # Update goal
        update_data = {
            "target_value": 25.0,
            "description": "Updated target"
        }
        response = await async_client.put(f"/api/v1/goals/{goal_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["target_value"] == 25.0
        assert result["description"] == "Updated target"

    @pytest.mark.asyncio
    async def test_update_progress(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating goal progress."""
        # Create goal first
        create_data = {
            "name": "Progress Test Goal",
            "metric_type": "engagement",
            "target_value": 1000.0,
            "current_value": 100.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]

        # Update progress
        progress_data = {
            "current_value": 250.0
        }
        response = await async_client.post(f"/api/v1/goals/{goal_id}/update-progress", json=progress_data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["current_value"] == 250.0
        assert result["progress_percentage"] == 25.0

    @pytest.mark.asyncio
    async def test_list_goals(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing goals."""
        response = await async_client.get("/api/v1/goals", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_goal_forecast(self, async_client: AsyncClient, auth_headers: dict):
        """Test goal forecasting."""
        # Create goal with some history
        create_data = {
            "name": "Forecast Test Goal",
            "metric_type": "revenue",
            "target_value": 50000.0,
            "current_value": 10000.0,
            "start_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]

        # Get forecast
        response = await async_client.get(f"/api/v1/goals/{goal_id}/forecast", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "forecast_value" in result
        assert "confidence" in result
        assert "on_track" in result

    @pytest.mark.asyncio
    async def test_goal_status_changes(self, async_client: AsyncClient, auth_headers: dict):
        """Test goal status lifecycle."""
        # Create goal
        create_data = {
            "name": "Status Test Goal",
            "metric_type": "conversion",
            "target_value": 100.0,
            "current_value": 0.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]
        assert create_response.json()["status"] == "active"

        # Update to achieved
        progress_data = {"current_value": 100.0}
        response = await async_client.post(f"/api/v1/goals/{goal_id}/update-progress", json=progress_data, headers=auth_headers)
        assert response.status_code == 200
        # Status should auto-update to achieved when target is met

    @pytest.mark.asyncio
    async def test_delete_goal(self, async_client: AsyncClient, auth_headers: dict):
        """Test deleting a goal."""
        # Create goal first
        create_data = {
            "name": "Delete Test Goal",
            "metric_type": "beneficiary",
            "target_value": 500.0,
            "current_value": 0.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/goals", json=create_data, headers=auth_headers)
        goal_id = create_response.json()["id"]

        # Delete goal
        response = await async_client.delete(f"/api/v1/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers)
        assert get_response.status_code == 404
