"""Pydantic schemas for Report model."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.report import ReportType, ReportFormat, ReportStatus


class ReportBase(BaseModel):
    """Base schema for Report."""
    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    report_type: ReportType = Field(..., description="Type of report")
    format: ReportFormat = Field(..., description="Report file format")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Report parameters")
    email_recipients: Optional[List[str]] = Field(None, description="Email addresses to send report to")


class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    created_by: UUID = Field(..., description="User who created the report")
    scheduled: Optional[bool] = Field(False, description="Is this a scheduled report")
    schedule_config: Optional[Dict[str, Any]] = Field(None, description="Cron schedule configuration")


class ReportUpdate(BaseModel):
    """Schema for updating a report."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[ReportStatus] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    email_recipients: Optional[List[str]] = None


class ReportResponse(ReportBase):
    """Schema for report responses."""
    id: UUID
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    scheduled: bool
    schedule_config: Optional[Dict[str, Any]] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleCreate(BaseModel):
    """Schema for scheduling a recurring report."""
    name: str = Field(..., min_length=1, max_length=255)
    report_type: ReportType
    format: ReportFormat
    parameters: Dict[str, Any] = Field(default_factory=dict)
    schedule_config: Dict[str, Any] = Field(
        ...,
        description="Cron schedule config with 'cron' key (e.g., {'cron': '0 0 * * *'})"
    )
    email_recipients: Optional[List[str]] = None
    created_by: UUID


class ReportEmailRequest(BaseModel):
    """Schema for emailing a report."""
    recipients: List[str] = Field(..., min_items=1, description="Email recipients")
    subject: Optional[str] = Field(None, description="Email subject")
    message: Optional[str] = Field(None, description="Email message body")
