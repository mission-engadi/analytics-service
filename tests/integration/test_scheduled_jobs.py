"""Integration tests for scheduled job endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime


class TestScheduledJobEndpoints:
    """Test scheduled job management."""

    @pytest.mark.asyncio
    async def test_create_scheduled_job(self, async_client: AsyncClient, auth_headers: dict):
        """Test creating a scheduled job."""
        data = {
            "name": "Daily Data Sync",
            "description": "Sync all service data daily",
            "job_type": "data_sync",
            "cron_expression": "0 2 * * *",  # Daily at 2 AM
            "config": {
                "services": ["partners_crm", "projects", "social_media"],
                "sync_type": "incremental"
            },
            "is_active": True
        }
        response = await async_client.post("/api/v1/scheduled-jobs", json=data, headers=auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert result["job_type"] == "data_sync"
        assert result["cron_expression"] == "0 2 * * *"
        assert result["is_active"] is True
        assert "next_run" in result

    @pytest.mark.asyncio
    async def test_get_scheduled_job(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieving a scheduled job."""
        # Create job first
        create_data = {
            "name": "Weekly Report Job",
            "job_type": "report_generation",
            "cron_expression": "0 9 * * 1",  # Monday at 9 AM
            "config": {"report_type": "weekly"},
            "is_active": True
        }
        create_response = await async_client.post("/api/v1/scheduled-jobs", json=create_data, headers=auth_headers)
        job_id = create_response.json()["id"]

        # Get job
        response = await async_client.get(f"/api/v1/scheduled-jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == job_id
        assert result["name"] == "Weekly Report Job"

    @pytest.mark.asyncio
    async def test_update_scheduled_job(self, async_client: AsyncClient, auth_headers: dict):
        """Test updating a scheduled job."""
        # Create job first
        create_data = {
            "name": "Update Test Job",
            "job_type": "goal_update",
            "cron_expression": "0 * * * *",  # Every hour
            "config": {},
            "is_active": True
        }
        create_response = await async_client.post("/api/v1/scheduled-jobs", json=create_data, headers=auth_headers)
        job_id = create_response.json()["id"]

        # Update job
        update_data = {
            "cron_expression": "0 */6 * * *",  # Every 6 hours
            "is_active": False
        }
        response = await async_client.put(f"/api/v1/scheduled-jobs/{job_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert result["cron_expression"] == "0 */6 * * *"
        assert result["is_active"] is False

    @pytest.mark.asyncio
    async def test_trigger_scheduled_job(self, async_client: AsyncClient, auth_headers: dict):
        """Test manually triggering a job."""
        # Create job first
        create_data = {
            "name": "Trigger Test Job",
            "job_type": "custom",
            "cron_expression": "0 0 * * *",
            "config": {"action": "test"},
            "is_active": True
        }
        create_response = await async_client.post("/api/v1/scheduled-jobs", json=create_data, headers=auth_headers)
        job_id = create_response.json()["id"]

        # Trigger job
        trigger_data = {
            "config_override": {"priority": "high"}
        }
        response = await async_client.post(f"/api/v1/scheduled-jobs/{job_id}/trigger", json=trigger_data, headers=auth_headers)
        assert response.status_code in [200, 202]  # Accepted for async execution

    @pytest.mark.asyncio
    async def test_list_scheduled_jobs(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing scheduled jobs."""
        response = await async_client.get("/api/v1/scheduled-jobs", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_job_execution_stats(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieving job execution statistics."""
        # Create and trigger job
        create_data = {
            "name": "Stats Test Job",
            "job_type": "data_sync",
            "cron_expression": "0 12 * * *",
            "config": {},
            "is_active": True
        }
        create_response = await async_client.post("/api/v1/scheduled-jobs", json=create_data, headers=auth_headers)
        job_id = create_response.json()["id"]

        # Get stats
        response = await async_client.get(f"/api/v1/scheduled-jobs/{job_id}/stats", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "total_executions" in result
        assert "successful_executions" in result
        assert "failed_executions" in result
        assert "success_rate" in result

    @pytest.mark.asyncio
    async def test_filter_jobs_by_type(self, async_client: AsyncClient, auth_headers: dict):
        """Test filtering jobs by type."""
        # Create jobs of different types
        job_types = ["data_sync", "report_generation", "goal_update"]
        for job_type in job_types:
            data = {
                "name": f"Filter Test {job_type}",
                "job_type": job_type,
                "cron_expression": "0 0 * * *",
                "config": {},
                "is_active": True
            }
            await async_client.post("/api/v1/scheduled-jobs", json=data, headers=auth_headers)

        # Filter by type
        response = await async_client.get("/api/v1/scheduled-jobs?job_type=data_sync", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert all(job["job_type"] == "data_sync" for job in result)

    @pytest.mark.asyncio
    async def test_delete_scheduled_job(self, async_client: AsyncClient, auth_headers: dict):
        """Test deleting a scheduled job."""
        # Create job first
        create_data = {
            "name": "Delete Test Job",
            "job_type": "custom",
            "cron_expression": "0 0 * * *",
            "config": {},
            "is_active": True
        }
        create_response = await async_client.post("/api/v1/scheduled-jobs", json=create_data, headers=auth_headers)
        job_id = create_response.json()["id"]

        # Delete job
        response = await async_client.delete(f"/api/v1/scheduled-jobs/{job_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(f"/api/v1/scheduled-jobs/{job_id}", headers=auth_headers)
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_cron_validation(self, async_client: AsyncClient, auth_headers: dict):
        """Test cron expression validation."""
        # Invalid cron expression
        data = {
            "name": "Invalid Cron Job",
            "job_type": "data_sync",
            "cron_expression": "invalid cron",
            "config": {},
            "is_active": True
        }
        response = await async_client.post("/api/v1/scheduled-jobs", json=data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
