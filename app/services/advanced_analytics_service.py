"""Service layer for advanced analytics operations."""
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.metric import Metric, ServiceName, MetricType
from app.schemas.advanced_analytics import (
    PredictionRequest,
    PredictionResponse,
    ForecastRequest,
    ForecastResponse,
    ComparisonRequest,
    ComparisonResponse,
    CustomCalculationRequest,
    CustomCalculationResponse,
)


class AdvancedAnalyticsService:
    """Service for advanced analytics including predictions and forecasting."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_predictions(self, request: PredictionRequest) -> PredictionResponse:
        """Generate predictions for metrics using trend analysis."""
        # Get historical data
        query = select(Metric).where(
            and_(
                Metric.service_name == request.service_name,
                Metric.metric_type == request.metric_type,
            )
        )

        if request.metric_name:
            query = query.where(Metric.metric_name == request.metric_name)

        query = query.order_by(Metric.timestamp.desc()).limit(90)
        result = await self.db.execute(query)
        historical_data = result.scalars().all()

        if not historical_data:
            # Return empty predictions if no data
            return PredictionResponse(
                service_name=request.service_name,
                metric_type=request.metric_type,
                metric_name=request.metric_name,
                predictions=[],
                confidence_level=request.confidence_level,
                model_accuracy=0.0,
                trend="stable",
            )

        # Extract values and calculate trend
        values = [m.value for m in reversed(historical_data)]
        
        # Simple linear regression for trend
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        # Determine trend
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"

        # Generate predictions
        predictions = []
        last_date = max([m.timestamp for m in historical_data])
        last_value = values[-1]

        for i in range(1, request.prediction_days + 1):
            pred_date = last_date + timedelta(days=i)
            # Linear prediction with some noise
            pred_value = slope * (len(values) + i) + intercept
            
            # Calculate confidence bounds (simplified)
            std_dev = np.std(values)
            margin = std_dev * (1 - request.confidence_level)
            
            predictions.append({
                "date": pred_date.date().isoformat(),
                "value": round(max(0, pred_value), 2),
                "lower_bound": round(max(0, pred_value - margin), 2),
                "upper_bound": round(pred_value + margin, 2),
            })

        # Calculate model accuracy (simplified)
        residuals = [values[i] - (slope * i + intercept) for i in range(len(values))]
        rmse = np.sqrt(np.mean(np.square(residuals)))
        accuracy = max(0, 1 - (rmse / np.mean(values))) if np.mean(values) > 0 else 0

        return PredictionResponse(
            service_name=request.service_name,
            metric_type=request.metric_type,
            metric_name=request.metric_name,
            predictions=predictions,
            confidence_level=request.confidence_level,
            model_accuracy=round(accuracy, 2),
            trend=trend,
        )

    async def get_forecasts(self, request: ForecastRequest) -> ForecastResponse:
        """Generate time-series forecasts."""
        # Get historical data aggregated by period
        period_map = {
            "day": 1,
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365,
        }
        days_per_period = period_map.get(request.forecast_period, 30)

        query = select(Metric).where(
            and_(
                Metric.service_name == request.service_name,
                Metric.metric_type == request.metric_type,
            )
        )

        if request.metric_name:
            query = query.where(Metric.metric_name == request.metric_name)

        result = await self.db.execute(query)
        historical_data = result.scalars().all()

        if not historical_data:
            return ForecastResponse(
                service_name=request.service_name,
                metric_type=request.metric_type,
                metric_name=request.metric_name,
                forecast_period=request.forecast_period,
                forecasts=[],
                historical_accuracy=0.0,
                seasonality_detected=False,
                trend_strength=0.0,
            )

        # Group by period and calculate
        values = [m.value for m in historical_data]
        
        # Calculate seasonality and trend
        seasonality_detected = self._detect_seasonality(values)
        trend_strength = abs(np.corrcoef(range(len(values)), values)[0, 1]) if len(values) > 1 else 0

        # Generate forecasts
        forecasts = []
        mean_value = np.mean(values)
        std_value = np.std(values)

        for i in range(1, request.periods_ahead + 1):
            # Simple forecast with trend
            if trend_strength > 0.5:
                growth_rate = (values[-1] - values[0]) / len(values) if len(values) > 0 else 0
                forecast_value = values[-1] + (growth_rate * i)
            else:
                forecast_value = mean_value

            # Add seasonal component if detected
            if seasonality_detected and len(values) >= 12:
                seasonal_index = i % 12
                seasonal_factor = values[seasonal_index] / mean_value if mean_value > 0 else 1
                forecast_value *= seasonal_factor

            confidence = max(0.5, 1 - (i * 0.02))  # Decrease confidence over time

            forecasts.append({
                "period": f"Period {i}",
                "value": round(max(0, forecast_value), 2),
                "confidence": round(confidence, 2),
            })

        return ForecastResponse(
            service_name=request.service_name,
            metric_type=request.metric_type,
            metric_name=request.metric_name,
            forecast_period=request.forecast_period,
            forecasts=forecasts,
            historical_accuracy=0.85,  # Placeholder
            seasonality_detected=seasonality_detected,
            trend_strength=round(trend_strength, 2),
        )

    async def get_comparisons(self, request: ComparisonRequest) -> ComparisonResponse:
        """Perform comparative analysis."""
        comparisons = []
        insights = []

        if request.comparison_type == "service":
            # Compare across services
            for service in ServiceName:
                query = select(func.sum(Metric.value)).where(
                    and_(
                        Metric.service_name == service,
                        Metric.metric_type == request.metric_type,
                    )
                )
                if request.metric_name:
                    query = query.where(Metric.metric_name == request.metric_name)
                if request.start_date:
                    query = query.where(Metric.date >= request.start_date)
                if request.end_date:
                    query = query.where(Metric.date <= request.end_date)

                result = await self.db.execute(query)
                total = result.scalar() or 0

                comparisons.append({
                    "label": service.value,
                    "value": float(total),
                })

        elif request.comparison_type == "time_period":
            # Compare time periods
            if request.start_date and request.end_date:
                period_length = (request.end_date - request.start_date).days
                
                for i in range(3):  # Compare 3 periods
                    period_start = request.start_date - timedelta(days=period_length * (i + 1))
                    period_end = request.start_date - timedelta(days=period_length * i) if i > 0 else request.end_date

                    query = select(func.sum(Metric.value)).where(
                        and_(
                            Metric.metric_type == request.metric_type,
                            Metric.date >= period_start,
                            Metric.date <= period_end,
                        )
                    )
                    if request.metric_name:
                        query = query.where(Metric.metric_name == request.metric_name)

                    result = await self.db.execute(query)
                    total = result.scalar() or 0

                    comparisons.append({
                        "label": f"Period {i + 1}: {period_start} to {period_end}",
                        "value": float(total),
                    })

        # Generate insights
        if comparisons:
            values = [c["value"] for c in comparisons]
            max_value = max(values)
            min_value = min(values)
            avg_value = sum(values) / len(values)

            best_performer = next(c["label"] for c in comparisons if c["value"] == max_value)
            worst_performer = next(c["label"] for c in comparisons if c["value"] == min_value)

            insights.append(f"Highest value: {max_value:.2f} ({best_performer})")
            insights.append(f"Lowest value: {min_value:.2f} ({worst_performer})")
            insights.append(f"Average value: {avg_value:.2f}")
            if max_value > 0:
                variance = ((max_value - min_value) / max_value) * 100
                insights.append(f"Variance: {variance:.1f}%")
        else:
            best_performer = None
            worst_performer = None
            insights.append("No data available for comparison")

        return ComparisonResponse(
            metric_type=request.metric_type,
            metric_name=request.metric_name,
            comparison_type=request.comparison_type,
            comparisons=comparisons,
            insights=insights,
            best_performer=best_performer,
            worst_performer=worst_performer,
        )

    async def custom_calculation(self, request: CustomCalculationRequest) -> CustomCalculationResponse:
        """Perform custom analytics calculations."""
        # Get data for calculation
        query = select(Metric).where(Metric.metric_type == request.metric_type)
        
        if request.metric_name:
            query = query.where(Metric.metric_name == request.metric_name)
        if request.start_date:
            query = query.where(Metric.date >= request.start_date)
        if request.end_date:
            query = query.where(Metric.date <= request.end_date)

        result = await self.db.execute(query)
        data = result.scalars().all()
        values = [m.value for m in data]

        results = {}
        interpretation = ""

        if request.calculation_type == "correlation":
            # Correlation with time
            if len(values) > 1:
                correlation = np.corrcoef(range(len(values)), values)[0, 1]
                results["correlation_coefficient"] = round(correlation, 3)
                results["correlation_strength"] = (
                    "strong" if abs(correlation) > 0.7
                    else "moderate" if abs(correlation) > 0.4
                    else "weak"
                )
                interpretation = f"The metric shows a {results['correlation_strength']} correlation with time."
            else:
                results["error"] = "Insufficient data for correlation analysis"
                interpretation = "Not enough data points for correlation analysis."

        elif request.calculation_type == "regression":
            # Linear regression
            if len(values) > 1:
                x = np.arange(len(values))
                coefficients = np.polyfit(x, values, 1)
                results["slope"] = round(coefficients[0], 3)
                results["intercept"] = round(coefficients[1], 3)
                results["equation"] = f"y = {results['slope']}x + {results['intercept']}"
                interpretation = f"Linear trend: {results['equation']}"
            else:
                results["error"] = "Insufficient data for regression analysis"
                interpretation = "Not enough data points for regression analysis."

        elif request.calculation_type == "anomaly_detection":
            # Simple anomaly detection using z-score
            if len(values) > 2:
                mean = np.mean(values)
                std = np.std(values)
                z_scores = [(v - mean) / std if std > 0 else 0 for v in values]
                anomalies = [i for i, z in enumerate(z_scores) if abs(z) > 2]
                
                results["anomaly_count"] = len(anomalies)
                results["anomaly_percentage"] = round((len(anomalies) / len(values)) * 100, 2)
                results["anomaly_indices"] = anomalies
                interpretation = f"Detected {len(anomalies)} anomalies ({results['anomaly_percentage']}% of data points)"
            else:
                results["error"] = "Insufficient data for anomaly detection"
                interpretation = "Not enough data points for anomaly detection."

        else:
            results["error"] = "Unknown calculation type"
            interpretation = "Calculation type not supported."

        return CustomCalculationResponse(
            calculation_type=request.calculation_type,
            metric_type=request.metric_type,
            metric_name=request.metric_name,
            results=results,
            visualizations=None,
            interpretation=interpretation,
        )

    def _detect_seasonality(self, values: List[float], period: int = 12) -> bool:
        """Detect seasonality in time series data."""
        if len(values) < period * 2:
            return False

        # Simple seasonality detection using autocorrelation
        mean = np.mean(values)
        variance = np.var(values)
        
        if variance == 0:
            return False

        autocorr = sum(
            (values[i] - mean) * (values[i + period] - mean)
            for i in range(len(values) - period)
        ) / (len(values) - period) / variance

        return autocorr > 0.5
