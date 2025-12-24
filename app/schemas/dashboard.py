"""Pydantic schemas for Dashboard model.

Schemas define the structure of API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.dashboard import DashboardType


class DashboardBase(BaseModel):
    """Base schema with common fields."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Dashboard name"
    )
    dashboard_type: DashboardType = Field(
        ...,
        description="Type of dashboard"
    )
    description: Optional[str] = Field(
        None,
        description="Dashboard description"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Dashboard configuration (widgets, layout, filters)"
    )
    is_default: bool = Field(
        False,
        description="Whether this is the default dashboard for its type"
    )
    is_public: bool = Field(
        False,
        description="Whether the dashboard is publicly accessible"
    )


class DashboardCreate(DashboardBase):
    """Schema for creating a dashboard.
    
    Used for POST requests.
    """
    
    created_by: uuid.UUID = Field(
        ...,
        description="User ID who created the dashboard"
    )


class DashboardUpdate(BaseModel):
    """Schema for updating a dashboard.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    dashboard_type: Optional[DashboardType] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None


class DashboardResponse(DashboardBase):
    """Schema for dashboard responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DashboardWidgetData(BaseModel):
    """Schema for dashboard widget data.
    
    Used for endpoints that return data for specific widgets.
    """
    
    widget_id: str = Field(..., description="Widget identifier")
    widget_type: str = Field(..., description="Type of widget (chart, table, metric, etc.)")
    data: Dict[str, Any] = Field(..., description="Widget data")
    updated_at: datetime = Field(..., description="When data was last updated")
