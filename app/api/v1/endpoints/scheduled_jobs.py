"""API endpoints for scheduled job management."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.scheduled_job import JobType
from app.schemas.scheduled_job import (
    ScheduledJobCreate,
    ScheduledJobUpdate,
    ScheduledJobResponse,
    ScheduledJobStats,
    JobTriggerRequest,
)
from app.services.scheduled_job_service import ScheduledJobService

router = APIRouter()


@router.post("", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: ScheduledJobCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new scheduled job.
    
    - **name**: Job name
    - **job_type**: Type of job (data_sync, report_generation, goal_update, custom)
    - **schedule**: Cron expression (e.g., "0 0 * * *" for daily at midnight)
    - **config**: Job configuration parameters
    - **is_active**: Whether the job is active (default: true)
    """
    service = ScheduledJobService(db)
    job = await service.create_job(job_data)
    return job


@router.get("/{job_id}", response_model=ScheduledJobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a scheduled job by ID.
    """
    service = ScheduledJobService(db)
    job = await service.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return job


@router.get("", response_model=List[ScheduledJobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    job_type: Optional[JobType] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List scheduled jobs with optional filters.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **job_type**: Filter by job type
    - **is_active**: Filter by active status
    """
    service = ScheduledJobService(db)
    jobs = await service.list_jobs(
        skip=skip,
        limit=limit,
        job_type=job_type,
        is_active=is_active,
    )
    return jobs


@router.put("/{job_id}", response_model=ScheduledJobResponse)
async def update_job(
    job_id: UUID,
    job_data: ScheduledJobUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a scheduled job.
    
    Can update:
    - Job name
    - Schedule (cron expression)
    - Active status
    - Configuration
    """
    service = ScheduledJobService(db)
    job = await service.update_job(job_id, job_data)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a scheduled job.
    """
    service = ScheduledJobService(db)
    deleted = await service.delete_job(job_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return None


@router.post("/{job_id}/trigger", status_code=status.HTTP_200_OK)
async def trigger_job(
    job_id: UUID,
    trigger_request: Optional[JobTriggerRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger a job execution.
    
    - **override_config**: Optional configuration override for this execution
    
    Returns execution status.
    """
    service = ScheduledJobService(db)
    success = await service.trigger_job(job_id, trigger_request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job execution failed",
        )
    
    return {"message": "Job triggered successfully", "status": "success"}


@router.get("/{job_id}/stats", response_model=ScheduledJobStats)
async def get_job_stats(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get execution statistics for a job.
    
    Returns:
    - Total runs
    - Successful/failed runs
    - Success rate
    - Last/next run times
    """
    service = ScheduledJobService(db)
    stats = await service.get_job_stats(job_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return stats
