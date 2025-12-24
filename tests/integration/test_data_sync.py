"""Integration tests for data sync endpoints."""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_sync import DataSync, SyncType, SyncStatus


class TestDataSyncEndpoints:
    """Test data synchronization endpoints."""

    @pytest.mark.asyncio
    async def test_trigger_sync(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test triggering a data sync."""
        sync_data = {
            "service_name": "partners_crm",
            "sync_type": "manual"
        }
        
        response = client.post(
            "/api/v1/sync",
            json=sync_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "partners_crm"
        assert data["sync_type"] == "manual"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_sync_status(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving sync status."""
        # Create a sync record
        sync = DataSync(
            service_name="partners_crm",
            sync_type=SyncType.manual,
            status=SyncStatus.running,
            start_time=datetime.utcnow()
        )
        db_session.add(sync)
        await db_session.commit()
        await db_session.refresh(sync)
        
        response = client.get(
            f"/api/v1/sync/{sync.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"

    @pytest.mark.asyncio
    async def test_list_syncs(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test listing sync records."""
        # Create multiple sync records
        for i in range(3):
            sync = DataSync(
                service_name="partners_crm",
                sync_type=SyncType.manual,
                status=SyncStatus.completed,
                start_time=datetime.utcnow(),
                completed_time=datetime.utcnow()
            )
            db_session.add(sync)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/sync",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_get_current_sync_status(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test getting current sync status for a service."""
        # Create a recent sync
        sync = DataSync(
            service_name="partners_crm",
            sync_type=SyncType.incremental,
            status=SyncStatus.completed,
            start_time=datetime.utcnow(),
            completed_time=datetime.utcnow(),
            records_processed=100
        )
        db_session.add(sync)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/sync/status",
            params={"service_name": "partners_crm"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "partners_crm"

    @pytest.mark.asyncio
    async def test_get_sync_statistics(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving sync statistics."""
        # Create sync records
        for i in range(5):
            sync = DataSync(
                service_name="partners_crm",
                sync_type=SyncType.incremental,
                status=SyncStatus.completed,
                start_time=datetime.utcnow(),
                completed_time=datetime.utcnow(),
                records_processed=100,
                records_failed=5
            )
            db_session.add(sync)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/sync/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_syncs" in data
        assert "total_records_processed" in data

    @pytest.mark.asyncio
    async def test_aggregate_all_services(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test triggering aggregation for all services."""
        response = client.post(
            "/api/v1/sync/aggregate-all",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "syncs" in data
