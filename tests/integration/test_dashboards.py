"""Integration tests for dashboard endpoints."""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import Dashboard, DashboardType


class TestDashboardEndpoints:
    """Test dashboard CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_dashboard(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test creating a new dashboard."""
        dashboard_data = {
            "name": "Test Dashboard",
            "dashboard_type": "custom",
            "description": "A test dashboard",
            "config": {
                "widgets": [
                    {"type": "metric", "position": {"x": 0, "y": 0}}
                ]
            },
            "created_by": "user-123",
            "is_default": False,
            "is_public": True
        }
        
        response = client.post(
            "/api/v1/dashboards",
            json=dashboard_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Dashboard"
        assert data["dashboard_type"] == "custom"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_dashboard(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving a dashboard by ID."""
        # Create a dashboard
        dashboard = Dashboard(
            name="Test Dashboard",
            dashboard_type=DashboardType.custom,
            created_by="user-123",
            config={"widgets": []}
        )
        db_session.add(dashboard)
        await db_session.commit()
        await db_session.refresh(dashboard)
        
        response = client.get(
            f"/api/v1/dashboards/{dashboard.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Dashboard"

    @pytest.mark.asyncio
    async def test_list_dashboards(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test listing dashboards."""
        # Create multiple dashboards
        for i in range(3):
            dashboard = Dashboard(
                name=f"Dashboard {i}",
                dashboard_type=DashboardType.custom,
                created_by="user-123",
                config={"widgets": []}
            )
            db_session.add(dashboard)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/dashboards",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_update_dashboard(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test updating a dashboard."""
        # Create a dashboard
        dashboard = Dashboard(
            name="Original Name",
            dashboard_type=DashboardType.custom,
            created_by="user-123",
            config={"widgets": []}
        )
        db_session.add(dashboard)
        await db_session.commit()
        await db_session.refresh(dashboard)
        
        # Update the dashboard
        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }
        response = client.put(
            f"/api/v1/dashboards/{dashboard.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_dashboard(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test deleting a dashboard."""
        # Create a dashboard
        dashboard = Dashboard(
            name="Delete Test",
            dashboard_type=DashboardType.custom,
            created_by="user-123",
            config={"widgets": []}
        )
        db_session.add(dashboard)
        await db_session.commit()
        await db_session.refresh(dashboard)
        
        # Delete the dashboard
        response = client.delete(
            f"/api/v1/dashboards/{dashboard.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_executive_dashboard(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving executive dashboard."""
        # Create an executive dashboard
        dashboard = Dashboard(
            name="Executive Dashboard",
            dashboard_type=DashboardType.executive,
            created_by="admin-123",
            config={"widgets": []},
            is_default=True
        )
        db_session.add(dashboard)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/dashboards/executive",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["dashboard_type"] == "executive"

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving dashboard data."""
        # Create a dashboard
        dashboard = Dashboard(
            name="Data Test",
            dashboard_type=DashboardType.custom,
            created_by="user-123",
            config={
                "widgets": [
                    {"type": "metric", "metric_name": "test_metric"}
                ]
            }
        )
        db_session.add(dashboard)
        await db_session.commit()
        await db_session.refresh(dashboard)
        
        response = client.get(
            f"/api/v1/dashboards/{dashboard.id}/data",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "widgets" in data
