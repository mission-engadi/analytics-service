"""API endpoints for advanced analytics."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
from app.services.advanced_analytics_service import AdvancedAnalyticsService

router = APIRouter()


@router.post("/predictions", response_model=PredictionResponse)
async def get_predictions(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate predictions for metrics using trend analysis.
    
    - **service_name**: Service to predict for
    - **metric_type**: Type of metric
    - **metric_name**: Optional specific metric name
    - **prediction_days**: Number of days to predict (1-365)
    - **confidence_level**: Confidence level for predictions (0.5-0.99)
    
    Returns:
    - Predicted values with confidence bounds
    - Model accuracy
    - Trend direction (increasing/decreasing/stable)
    """
    service = AdvancedAnalyticsService(db)
    
    try:
        predictions = await service.get_predictions(request)
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction generation failed: {str(e)}",
        )


@router.post("/forecasts", response_model=ForecastResponse)
async def get_forecasts(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate time-series forecasts.
    
    - **service_name**: Service to forecast for
    - **metric_type**: Type of metric
    - **metric_name**: Optional specific metric name
    - **forecast_period**: Period (day, week, month, quarter, year)
    - **periods_ahead**: Number of periods to forecast (1-24)
    
    Returns:
    - Forecasted values by period
    - Historical accuracy
    - Seasonality detection
    - Trend strength
    """
    service = AdvancedAnalyticsService(db)
    
    try:
        forecasts = await service.get_forecasts(request)
        return forecasts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}",
        )


@router.post("/comparisons", response_model=ComparisonResponse)
async def get_comparisons(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Perform comparative analysis.
    
    - **metric_type**: Type of metric to compare
    - **metric_name**: Optional specific metric name
    - **comparison_type**: Type of comparison (service, time_period, segment)
    - **start_date**: Optional start date for filtering
    - **end_date**: Optional end date for filtering
    - **segments**: Optional segments to compare
    
    Returns:
    - Comparison data
    - Key insights
    - Best/worst performers
    """
    service = AdvancedAnalyticsService(db)
    
    try:
        comparisons = await service.get_comparisons(request)
        return comparisons
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison analysis failed: {str(e)}",
        )


@router.post("/calculate", response_model=CustomCalculationResponse)
async def custom_calculation(
    request: CustomCalculationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Perform custom analytics calculations.
    
    - **calculation_type**: Type of calculation:
      - correlation: Correlation analysis
      - regression: Linear regression
      - clustering: Cluster analysis
      - anomaly_detection: Detect anomalies
    - **metric_type**: Type of metric
    - **metric_name**: Optional specific metric name
    - **parameters**: Additional calculation parameters
    - **start_date**: Optional start date
    - **end_date**: Optional end date
    
    Returns:
    - Calculation results
    - Suggested visualizations
    - Human-readable interpretation
    """
    service = AdvancedAnalyticsService(db)
    
    try:
        results = await service.custom_calculation(request)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom calculation failed: {str(e)}",
        )
