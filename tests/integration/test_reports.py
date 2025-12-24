"""Integration tests for report endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


class TestReportEndpoints:
    """Test report generation and management."""

    @pytest.mark.asyncio
    async def test_create_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test report creation."""
        data = {
            "name": "Monthly Donations Report",
            "report_type": "monthly",
            "format": "pdf",
            "parameters": {
                "service_name": "partners_crm",
                "metric_type": "donation",
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "created_by": "test-user-123"
        }
        response = await async_client.post("/api/v1/reports/generate", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert result["report_type"] == "monthly"
        assert result["format"] == "pdf"
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieving a report."""
        # Create report first
        create_data = {
            "name": "Weekly Report",
            "report_type": "weekly",
            "format": "excel",
            "parameters": {},
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/reports/generate", json=create_data, headers=auth_headers)
        report_id = create_response.json()["id"]

        # Get report
        response = await async_client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == report_id
        assert result["name"] == "Weekly Report"

    @pytest.mark.asyncio
    async def test_list_reports(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing reports."""
        response = await async_client.get("/api/v1/reports", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_schedule_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test scheduling a report."""
        data = {
            "name": "Daily Scheduled Report",
            "report_type": "daily",
            "format": "csv",
            "parameters": {},
            "scheduled": True,
            "schedule_config": {
                "cron": "0 8 * * *",  # Daily at 8 AM
                "timezone": "UTC"
            },
            "recipients": ["test@example.com"],
            "created_by": "test-user-123"
        }
        response = await async_client.post("/api/v1/reports/schedule", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["scheduled"] is True
        assert result["schedule_config"]["cron"] == "0 8 * * *"

    @pytest.mark.asyncio
    async def test_email_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test emailing a report."""
        # Create report first
        create_data = {
            "name": "Email Test Report",
            "report_type": "custom",
            "format": "pdf",
            "parameters": {},
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/reports/generate", json=create_data, headers=auth_headers)
        report_id = create_response.json()["id"]

        # Email report
        email_data = {
            "recipients": ["test@example.com", "test2@example.com"],
            "subject": "Analytics Report",
            "message": "Please find attached report"
        }
        response = await async_client.post(f"/api/v1/reports/{report_id}/email", json=email_data, headers=auth_headers)
        assert response.status_code in [200, 202]  # Accepted for async processing

    @pytest.mark.asyncio
    async def test_delete_report(self, async_client: AsyncClient, auth_headers: dict):
        """Test deleting a report."""
        # Create report first
        create_data = {
            "name": "Delete Test Report",
            "report_type": "annual",
            "format": "json",
            "parameters": {},
            "created_by": "test-user-123"
        }
        create_response = await async_client.post("/api/v1/reports/generate", json=create_data, headers=auth_headers)
        report_id = create_response.json()["id"]

        # Delete report
        response = await async_client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_report_formats(self, async_client: AsyncClient, auth_headers: dict):
        """Test different report formats."""
        formats = ["pdf", "excel", "csv", "json"]
        for fmt in formats:
            data = {
                "name": f"Format Test {fmt}",
                "report_type": "daily",
                "format": fmt,
                "parameters": {},
                "created_by": "test-user-123"
            }
            response = await async_client.post("/api/v1/reports/generate", json=data, headers=auth_headers)
            assert response.status_code == 201
            assert response.json()["format"] == fmt
