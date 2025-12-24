"""API endpoints for report management."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.report import ReportType, ReportStatus
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportScheduleCreate,
    ReportEmailRequest,
)
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new analytics report.
    
    - **name**: Report name
    - **report_type**: Type of report (daily, weekly, monthly, annual, custom)
    - **format**: Report format (pdf, excel, csv, json)
    - **parameters**: Report parameters and filters
    - **email_recipients**: Optional email addresses to send report to
    """
    service = ReportService(db)
    report = await service.create_report(report_data)
    
    # Trigger report generation
    report = await service.generate_report(report.id)
    
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a report by ID.
    """
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    return report


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[ReportType] = None,
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    scheduled: Optional[bool] = None,
    created_by: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List reports with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **report_type**: Filter by report type
    - **status**: Filter by report status
    - **scheduled**: Filter by scheduled reports
    - **created_by**: Filter by creator user ID
    """
    service = ReportService(db)
    reports = await service.list_reports(
        skip=skip,
        limit=limit,
        report_type=report_type,
        status=status_filter,
        scheduled=scheduled,
        created_by=created_by,
    )
    return reports


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a report and its associated file.
    """
    service = ReportService(db)
    deleted = await service.delete_report(report_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    return None


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the generated report file.
    """
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    if not report.file_path or report.status != ReportStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report file is not available",
        )
    
    return FileResponse(
        path=report.file_path,
        filename=f"{report.name}.{report.format.value}",
        media_type="application/octet-stream",
    )


@router.post("/{report_id}/email", status_code=status.HTTP_200_OK)
async def email_report(
    report_id: UUID,
    email_request: ReportEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a report via email.
    
    - **recipients**: List of email addresses
    - **subject**: Optional email subject
    - **message**: Optional email message body
    """
    service = ReportService(db)
    success = await service.email_report(report_id, email_request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to email report",
        )
    
    return {"message": "Report emailed successfully"}


@router.post("/schedule", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def schedule_report(
    schedule_data: ReportScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule a recurring report.
    
    - **schedule_config**: Cron schedule configuration
    - Example: {"cron": "0 0 * * *"} for daily at midnight
    """
    service = ReportService(db)
    report = await service.schedule_report(schedule_data)
    return report
