"""Pydantic schemas for Metric model.

Schemas define the structure of API requests and responses.
"""

import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.metric import ServiceName, MetricType


class MetricBase(BaseModel):
    """Base schema with common fields."""
    
    service_name: ServiceName = Field(
        ...,
        description="Service that generated the metric"
    )
    metric_type: MetricType = Field(
        ...,
        description="Type of metric"
    )
    metric_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the metric"
    )
    metric_value: float = Field(
        ...,
        description="Numeric value of the metric"
    )
    metric_unit: Optional[str] = Field(
        None,
        max_length=50,
        description="Unit of measurement (USD, count, percentage, etc.)"
    )
    dimensions: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional dimensions (partner_type, project_type, channel, etc.)"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when metric was recorded"
    )
    date: date = Field(
        ...,
        description="Date for daily aggregations"
    )
    meta: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context"
    )


class MetricCreate(MetricBase):
    """Schema for creating a metric.
    
    Used for POST requests.
    """
    pass


class MetricUpdate(BaseModel):
    """Schema for updating a metric.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    service_name: Optional[ServiceName] = None
    metric_type: Optional[MetricType] = None
    metric_name: Optional[str] = Field(None, min_length=1, max_length=255)
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = Field(None, max_length=50)
    dimensions: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    date: Optional[date] = None
    meta: Optional[Dict[str, Any]] = None


class MetricResponse(MetricBase):
    """Schema for metric responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    created_at: datetime


class MetricAggregation(BaseModel):
    """Schema for aggregated metric data.
    
    Used for analytics endpoints that return aggregated metrics.
    """
    
    metric_name: str
    metric_type: MetricType
    total: float
    average: float
    min_value: float
    max_value: float
    count: int
    date_range: Dict[str, date]
    dimensions: Optional[Dict[str, Any]] = None
