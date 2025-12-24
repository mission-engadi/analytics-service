"""Integration tests for partner analytics endpoints."""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.models.metric import Metric, ServiceName, MetricType


class TestPartnerAnalyticsEndpoints:
    """Test partner analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_partner_statistics(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving partner statistics."""
        # Create some partner metrics
        for i in range(3):
            metric = Metric(
                service_name=ServiceName.partners_crm,
                metric_type=MetricType.partner,
                metric_name="active_partners",
                value=10.0,
                timestamp=datetime.utcnow(),
                date=date.today()
            )
            db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/analytics/partners/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_donation_trends(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving donation trends."""
        # Create donation metrics
        for i in range(5):
            metric = Metric(
                service_name=ServiceName.partners_crm,
                metric_type=MetricType.donation,
                metric_name="total_donations",
                value=1000.0 * (i + 1),
                timestamp=datetime.utcnow(),
                date=date.today()
            )
            db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/analytics/partners/donations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_engagement_metrics(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving engagement metrics."""
        # Create engagement metrics
        metric = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.engagement,
            metric_name="partner_engagement",
            value=85.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/analytics/partners/engagement",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_partner_breakdown(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test retrieving partner type breakdown."""
        response = client.get(
            "/api/v1/analytics/partners/breakdown",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_partner_statistics_with_date_filter(self, client: TestClient, auth_headers: dict, db_session: AsyncSession):
        """Test partner statistics with date filtering."""
        # Create metrics
        metric = Metric(
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.partner,
            metric_name="new_partners",
            value=5.0,
            timestamp=datetime.utcnow(),
            date=date.today()
        )
        db_session.add(metric)
        await db_session.commit()
        
        response = client.get(
            "/api/v1/analytics/partners/statistics",
            params={
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat()
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
