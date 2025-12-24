"""Pydantic schemas for ScheduledJob model."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.scheduled_job import JobType, JobStatus


class ScheduledJobBase(BaseModel):
    """Base schema for ScheduledJob."""
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    job_type: JobType = Field(..., description="Type of job")
    schedule: str = Field(
        ...,
        min_length=9,
        max_length=100,
        description="Cron expression (e.g., '0 0 * * *')"
    )
    config: Dict[str, Any] = Field(default_factory=dict, description="Job configuration")


class ScheduledJobCreate(ScheduledJobBase):
    """Schema for creating a new scheduled job."""
    is_active: Optional[bool] = Field(True, description="Is the job active")


class ScheduledJobUpdate(BaseModel):
    """Schema for updating a scheduled job."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    schedule: Optional[str] = Field(None, min_length=9, max_length=100)
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ScheduledJobResponse(ScheduledJobBase):
    """Schema for scheduled job responses."""
    id: UUID
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    last_status: Optional[JobStatus] = None
    run_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduledJobStats(BaseModel):
    """Schema for job execution statistics."""
    job_id: UUID
    job_name: str
    job_type: JobType
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    average_duration: Optional[float] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None


class JobTriggerRequest(BaseModel):
    """Schema for manually triggering a job."""
    override_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Override job configuration for this execution"
    )
