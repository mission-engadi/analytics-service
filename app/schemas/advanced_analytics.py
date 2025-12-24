"""Pydantic schemas for Advanced Analytics endpoints."""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.metric import ServiceName, MetricType


class PredictionRequest(BaseModel):
    """Schema for prediction requests."""
    service_name: ServiceName
    metric_type: MetricType
    metric_name: Optional[str] = None
    prediction_days: int = Field(default=30, ge=1, le=365, description="Days to predict")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99, description="Confidence level")


class PredictionResponse(BaseModel):
    """Schema for prediction responses."""
    service_name: ServiceName
    metric_type: MetricType
    metric_name: Optional[str]
    predictions: List[Dict[str, Any]] = Field(
        ...,
        description="List of predictions with date, value, lower_bound, upper_bound"
    )
    confidence_level: float
    model_accuracy: float
    trend: str = Field(..., description="increasing, decreasing, or stable")


class ForecastRequest(BaseModel):
    """Schema for forecast requests."""
    service_name: ServiceName
    metric_type: MetricType
    metric_name: Optional[str] = None
    forecast_period: str = Field(
        default="month",
        description="Forecast period: day, week, month, quarter, year"
    )
    periods_ahead: int = Field(default=12, ge=1, le=24, description="Number of periods to forecast")


class ForecastResponse(BaseModel):
    """Schema for forecast responses."""
    service_name: ServiceName
    metric_type: MetricType
    metric_name: Optional[str]
    forecast_period: str
    forecasts: List[Dict[str, Any]] = Field(
        ...,
        description="List of forecasts with period, value, confidence"
    )
    historical_accuracy: float
    seasonality_detected: bool
    trend_strength: float


class ComparisonRequest(BaseModel):
    """Schema for comparison requests."""
    metric_type: MetricType
    metric_name: Optional[str] = None
    comparison_type: str = Field(
        default="service",
        description="Comparison type: service, time_period, segment"
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    segments: Optional[List[str]] = Field(None, description="Segments to compare")


class ComparisonResponse(BaseModel):
    """Schema for comparison responses."""
    metric_type: MetricType
    metric_name: Optional[str]
    comparison_type: str
    comparisons: List[Dict[str, Any]] = Field(
        ...,
        description="Comparison data with labels and values"
    )
    insights: List[str] = Field(..., description="Key insights from comparison")
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None


class CustomCalculationRequest(BaseModel):
    """Schema for custom calculation requests."""
    calculation_type: str = Field(
        ...,
        description="Type: correlation, regression, clustering, anomaly_detection"
    )
    metric_type: MetricType
    metric_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Calculation parameters")
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CustomCalculationResponse(BaseModel):
    """Schema for custom calculation responses."""
    calculation_type: str
    metric_type: MetricType
    metric_name: Optional[str]
    results: Dict[str, Any] = Field(..., description="Calculation results")
    visualizations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Suggested visualizations for results"
    )
    interpretation: str = Field(..., description="Human-readable interpretation")
