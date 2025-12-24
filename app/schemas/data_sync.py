"""Pydantic schemas for DataSync model.

Schemas define the structure of API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.data_sync import ServiceName, SyncType, SyncStatus


class DataSyncBase(BaseModel):
    """Base schema with common fields."""
    
    service_name: ServiceName = Field(
        ...,
        description="Service being synchronized"
    )
    sync_type: SyncType = Field(
        ...,
        description="Type of synchronization"
    )
    meta: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )


class DataSyncCreate(DataSyncBase):
    """Schema for creating a data sync.
    
    Used for POST requests.
    """
    pass


class DataSyncUpdate(BaseModel):
    """Schema for updating a data sync.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    status: Optional[SyncStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: Optional[int] = Field(None, ge=0)
    records_failed: Optional[int] = Field(None, ge=0)
    last_sync_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class DataSyncResponse(DataSyncBase):
    """Schema for data sync responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    status: SyncStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int
    records_failed: int
    last_sync_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DataSyncStats(BaseModel):
    """Schema for data sync statistics.
    
    Used for endpoints that return sync statistics.
    """
    
    service_name: ServiceName
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    total_records_processed: int
    total_records_failed: int
    last_sync_at: Optional[datetime] = None
    average_duration_seconds: Optional[float] = None
