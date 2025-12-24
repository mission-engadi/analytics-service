"""Integration tests for advanced analytics endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


class TestAdvancedAnalyticsEndpoints:
    """Test advanced analytics and predictions."""

    @pytest.mark.asyncio
    async def test_get_predictions(self, async_client: AsyncClient, auth_headers: dict):
        """Test metric predictions."""
        params = {
            "service_name": "partners_crm",
            "metric_type": "donation",
            "days": 30
        }
        response = await async_client.get("/api/v1/analytics/advanced/predictions", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "predictions" in result
        assert "trend" in result
        assert "confidence" in result
        assert isinstance(result["predictions"], list)

    @pytest.mark.asyncio
    async def test_get_forecasts(self, async_client: AsyncClient, auth_headers: dict):
        """Test time-series forecasts."""
        params = {
            "service_name": "projects",
            "metric_type": "project",
            "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "forecast_days": 30
        }
        response = await async_client.get("/api/v1/analytics/advanced/forecasts", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "historical" in result
        assert "forecast" in result
        assert "seasonality" in result
        assert len(result["forecast"]) > 0

    @pytest.mark.asyncio
    async def test_get_comparisons(self, async_client: AsyncClient, auth_headers: dict):
        """Test comparative analysis."""
        params = {
            "metric_type": "engagement",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "compare_to_previous_period": True
        }
        response = await async_client.get("/api/v1/analytics/advanced/comparisons", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "current_period" in result
        assert "previous_period" in result
        assert "change_percentage" in result
        assert "trend" in result

    @pytest.mark.asyncio
    async def test_custom_calculations(self, async_client: AsyncClient, auth_headers: dict):
        """Test custom metric calculations."""
        data = {
            "calculation_type": "average",
            "service_name": "social_media",
            "metric_type": "social_post",
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "group_by": "date"
        }
        response = await async_client.post("/api/v1/analytics/advanced/custom-calculations", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        assert "calculation_type" in result
        assert isinstance(result["result"], (int, float, dict, list))

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, async_client: AsyncClient, auth_headers: dict):
        """Test anomaly detection in metrics."""
        params = {
            "service_name": "notification",
            "metric_type": "notification",
            "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "sensitivity": 0.95
        }
        response = await async_client.get("/api/v1/analytics/advanced/anomalies", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "anomalies" in result
        assert "threshold" in result
        assert isinstance(result["anomalies"], list)

    @pytest.mark.asyncio
    async def test_trend_analysis(self, async_client: AsyncClient, auth_headers: dict):
        """Test trend analysis."""
        params = {
            "service_name": "partners_crm",
            "metric_type": "partner",
            "start_date": (datetime.now() - timedelta(days=180)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "interval": "week"
        }
        response = await async_client.get("/api/v1/analytics/advanced/trends", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "trend" in result
        assert "direction" in result
        assert "strength" in result
        assert result["direction"] in ["up", "down", "stable"]

    @pytest.mark.asyncio
    async def test_correlation_analysis(self, async_client: AsyncClient, auth_headers: dict):
        """Test correlation between metrics."""
        data = {
            "metric1": {
                "service_name": "partners_crm",
                "metric_type": "donation"
            },
            "metric2": {
                "service_name": "social_media",
                "metric_type": "engagement"
            },
            "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        response = await async_client.post("/api/v1/analytics/advanced/correlations", json=data, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "correlation" in result
        assert "strength" in result
        assert -1.0 <= result["correlation"] <= 1.0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, async_client: AsyncClient, auth_headers: dict):
        """Test performance benchmarking."""
        params = {
            "metric_type": "conversion",
            "period": "month"
        }
        response = await async_client.get("/api/v1/analytics/advanced/benchmarks", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "average" in result
        assert "median" in result
        assert "percentiles" in result
        assert "best" in result
        assert "worst" in result

    @pytest.mark.asyncio
    async def test_prediction_confidence_levels(self, async_client: AsyncClient, auth_headers: dict):
        """Test predictions with different confidence levels."""
        confidence_levels = [0.80, 0.90, 0.95]
        for confidence in confidence_levels:
            params = {
                "service_name": "projects",
                "metric_type": "beneficiary",
                "days": 14,
                "confidence": confidence
            }
            response = await async_client.get("/api/v1/analytics/advanced/predictions", params=params, headers=auth_headers)
            assert response.status_code == 200
            result = response.json()
            assert result["confidence"] == confidence

    @pytest.mark.asyncio
    async def test_data_quality_metrics(self, async_client: AsyncClient, auth_headers: dict):
        """Test data quality assessment."""
        params = {
            "service_name": "notification",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        response = await async_client.get("/api/v1/analytics/advanced/data-quality", params=params, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert "completeness" in result
        assert "consistency" in result
        assert "timeliness" in result
        assert 0 <= result["completeness"] <= 100
