"""Integration tests for metric endpoints."""
import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric, ServiceName, MetricType


class TestMetricEndpoints:
    """Test metric CRUD and aggregation endpoints."""

    @pytest.mark.asyncio
    async def test_create_metric(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test creating a new metric."""
        metric_data = {
            "service_name": "partners_crm",
            "metric_type": "donation",
            "metric_name": "total_donations",
            "value": 5000.50,
            "timestamp": datetime.utcnow().isoformat(),
            "dimensions": {"partner_type": "individual"},
            "meta": {"currency": "USD"}
        }
        
        response = client.post(
            "/api/v1/metrics",
            json=metric_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metric_name"] == "total_donations"
        assert data["value"] == 5000.50
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_metric(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving a metric by ID."""
        # Create a metric first
        metric = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.donation,
            metric_name="test_metric",
            value=100.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add(metric)
        await db_session.commit()
        await db_session.refresh(metric)
        
        response = client.get(
            f"/api/v1/metrics/{metric.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metric_name"] == "test_metric"
        assert data["value"] == 100.0

    @pytest.mark.asyncio
    async def test_list_metrics(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test listing metrics with filters."""
        # Create multiple metrics
        for i in range(3):
            metric = Metric(
                service_name=ServiceName.partners_crm,
                metric_type=MetricType.donation,
                metric_name=f"metric_{i}",
                value=100.0 * (i + 1),
                timestamp=datetime.utcnow(),
                date=date.today()
            )
            db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_update_metric(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test updating a metric."""
        # Create a metric
        metric = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.donation,
            metric_name="update_test",
            value=100.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add(metric)
        await db_session.commit()
        await db_session.refresh(metric)
        
        # Update the metric
        update_data = {"value": 200.0}
        response = client.patch(
            f"/api/v1/metrics/{metric.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 200.0

    @pytest.mark.asyncio
    async def test_delete_metric(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test deleting a metric."""
        # Create a metric
        metric = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.donation,
            metric_name="delete_test",
            value=100.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add(metric)
        await db_session.commit()
        await db_session.refresh(metric)
        
        # Delete the metric
        response = client.delete(
            f"/api/v1/metrics/{metric.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_aggregate_metrics(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test metric aggregation."""
        # Create metrics for aggregation
        for i in range(5):
            metric = Metric(
                service_name=ServiceName.partners_crm,
                metric_type=MetricType.donation,
                metric_name="donations",
                value=100.0,
                timestamp=datetime.utcnow(),
                date=date.today()
            )
            db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/metrics/aggregate",
            params={"service_name": "partners_crm", "metric_type": "donation"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sum" in data
        assert "avg" in data
        assert data["count"] >= 5

    @pytest.mark.asyncio
    async def test_get_metrics_by_service(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test filtering metrics by service."""
        # Create metrics for different services
        metric1 = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.donation,
            metric_name="test1",
            value=100.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        metric2 = Metric(
            service_name=ServiceName.projects,
            metric_type=MetricType.project,
            metric_name="test2",
            value=200.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add_all([metric1, metric2])
        await db_session.commit()
        
        response = client.get(
            "/api/v1/metrics/by-service/partners_crm",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(m["service_name"] == "partners_crm" for m in data)

    @pytest.mark.asyncio
    async def test_get_time_series(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test time series data retrieval."""
        # Create metrics over time
        for i in range(3):
            metric = Metric(
                service_name=ServiceName.partners_crm,
                metric_type=MetricType.donation,
                metric_name="timeseries_test",
                value=100.0 * (i + 1),
                timestamp=datetime.utcnow(),
                date=date.today()
            )
            db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/metrics/time-series",
            params={
                "metric_name": "timeseries_test",
                "interval": "day"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
