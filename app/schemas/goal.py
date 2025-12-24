"""Pydantic schemas for Goal model."""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.goal import GoalMetricType, GoalStatus


class GoalBase(BaseModel):
    """Base schema for Goal."""
    name: str = Field(..., min_length=1, max_length=255, description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    metric_type: GoalMetricType = Field(..., description="Type of metric being tracked")
    target_value: float = Field(..., gt=0, description="Target value to achieve")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    start_date: date = Field(..., description="Goal start date")
    end_date: date = Field(..., description="Goal end date")
    alert_threshold: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Alert when progress reaches this percentage"
    )


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""
    created_by: UUID = Field(..., description="User who created the goal")
    current_value: Optional[float] = Field(0.0, ge=0, description="Initial progress value")


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_value: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    end_date: Optional[date] = None
    status: Optional[GoalStatus] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)


class GoalProgressUpdate(BaseModel):
    """Schema for updating goal progress."""
    current_value: float = Field(..., ge=0, description="New progress value")


class GoalResponse(GoalBase):
    """Schema for goal responses."""
    id: UUID
    current_value: float
    status: GoalStatus
    progress_percentage: float
    alert_sent: bool
    forecast_value: Optional[float] = None
    forecast_updated_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoalProgressResponse(BaseModel):
    """Schema for goal progress details."""
    goal_id: UUID
    goal_name: str
    metric_type: GoalMetricType
    target_value: float
    current_value: float
    unit: Optional[str]
    progress_percentage: float
    status: GoalStatus
    days_remaining: int
    daily_required_progress: Optional[float] = None
    on_track: bool
    forecast_value: Optional[float] = None
    forecast_updated_at: Optional[datetime] = None


class GoalForecastResponse(BaseModel):
    """Schema for goal forecast details."""
    goal_id: UUID
    goal_name: str
    current_value: float
    target_value: float
    forecast_value: float
    forecast_confidence: float
    will_achieve: bool
    projected_completion_date: Optional[date] = None
    recommended_action: str
