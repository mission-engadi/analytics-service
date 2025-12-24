"""Service layer for scheduled job operations."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.scheduled_job import ScheduledJob, JobType, JobStatus
from app.schemas.scheduled_job import (
    ScheduledJobCreate,
    ScheduledJobUpdate,
    ScheduledJobStats,
    JobTriggerRequest,
)


class ScheduledJobService:
    """Service for managing scheduled background jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, job_data: ScheduledJobCreate) -> ScheduledJob:
        """Create a new scheduled job."""
        job = ScheduledJob(
            name=job_data.name,
            job_type=job_data.job_type,
            schedule=job_data.schedule,
            is_active=job_data.is_active if job_data.is_active is not None else True,
            config=job_data.config,
            next_run_at=self._calculate_next_run(job_data.schedule),
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: UUID) -> Optional[ScheduledJob]:
        """Get a job by ID."""
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        job_type: Optional[JobType] = None,
        is_active: Optional[bool] = None,
    ) -> List[ScheduledJob]:
        """List scheduled jobs with filters."""
        query = select(ScheduledJob)
        filters = []

        if job_type:
            filters.append(ScheduledJob.job_type == job_type)
        if is_active is not None:
            filters.append(ScheduledJob.is_active == is_active)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(ScheduledJob.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_job(self, job_id: UUID, job_data: ScheduledJobUpdate) -> Optional[ScheduledJob]:
        """Update a scheduled job."""
        job = await self.get_job(job_id)
        if not job:
            return None

        update_data = job_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        # Recalculate next run if schedule changed
        if 'schedule' in update_data:
            job.next_run_at = self._calculate_next_run(job.schedule)

        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete_job(self, job_id: UUID) -> bool:
        """Delete a scheduled job."""
        job = await self.get_job(job_id)
        if not job:
            return False

        await self.db.delete(job)
        await self.db.commit()
        return True

    async def trigger_job(self, job_id: UUID, trigger_request: Optional[JobTriggerRequest] = None) -> bool:
        """Manually trigger a job execution."""
        job = await self.get_job(job_id)
        if not job:
            return False

        # Update job status
        job.last_run_at = datetime.utcnow()
        job.last_status = JobStatus.running
        job.run_count += 1
        await self.db.commit()

        try:
            # Execute job based on type
            config = (
                {**job.config, **trigger_request.override_config}
                if trigger_request and trigger_request.override_config
                else job.config
            )

            await self._execute_job(job.job_type, config)

            # Update success
            job.last_status = JobStatus.success
            job.success_count += 1
            job.next_run_at = self._calculate_next_run(job.schedule)

        except Exception as e:
            # Update failure
            job.last_status = JobStatus.failed
            job.failure_count += 1
            print(f"Job execution failed: {e}")

        await self.db.commit()
        return job.last_status == JobStatus.success

    async def get_job_stats(self, job_id: UUID) -> Optional[ScheduledJobStats]:
        """Get execution statistics for a job."""
        job = await self.get_job(job_id)
        if not job:
            return None

        success_rate = (
            (job.success_count / job.run_count * 100)
            if job.run_count > 0
            else 0.0
        )

        return ScheduledJobStats(
            job_id=job.id,
            job_name=job.name,
            job_type=job.job_type,
            total_runs=job.run_count,
            successful_runs=job.success_count,
            failed_runs=job.failure_count,
            success_rate=round(success_rate, 2),
            average_duration=None,  # Would need execution time tracking
            last_run_at=job.last_run_at,
            next_run_at=job.next_run_at,
        )

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from cron expression (simplified)."""
        # This is a simplified implementation
        # In production, use a library like croniter

        now = datetime.utcnow()

        # Parse simple cron patterns
        if schedule == "@hourly" or schedule == "0 * * * *":
            return now + timedelta(hours=1)
        elif schedule == "@daily" or schedule == "0 0 * * *":
            return now + timedelta(days=1)
        elif schedule == "@weekly" or schedule == "0 0 * * 0":
            return now + timedelta(weeks=1)
        elif schedule == "@monthly":
            return now + timedelta(days=30)
        else:
            # Default to hourly if can't parse
            return now + timedelta(hours=1)

    async def _execute_job(self, job_type: JobType, config: Dict[str, Any]) -> None:
        """Execute job based on type (placeholder for actual implementation)."""
        # In production, this would trigger actual job execution
        # For now, just simulate execution
        if job_type == JobType.data_sync:
            print(f"Executing data sync job with config: {config}")
        elif job_type == JobType.report_generation:
            print(f"Executing report generation job with config: {config}")
        elif job_type == JobType.goal_update:
            print(f"Executing goal update job with config: {config}")
        else:
            print(f"Executing custom job with config: {config}")
