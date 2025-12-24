"""Scheduled job model for background tasks."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db.base_class import Base


class JobType(str, enum.Enum):
    """Types of scheduled jobs."""
    data_sync = "data_sync"
    report_generation = "report_generation"
    goal_update = "goal_update"
    custom = "custom"


class JobStatus(str, enum.Enum):
    """Job execution status."""
    success = "success"
    failed = "failed"
    running = "running"
    pending = "pending"


class ScheduledJob(Base):
    """Scheduled job model for managing background tasks.
    
    Stores job configuration, scheduling information, and execution history.
    Supports cron expressions for flexible scheduling.
    """
    __tablename__ = "scheduled_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Job name")
    job_type = Column(
        Enum(JobType, name="job_type_enum"),
        nullable=False,
        index=True,
        comment="Type of job"
    )
    schedule = Column(
        String(100),
        nullable=False,
        comment="Cron expression for job schedule"
    )
    is_active = Column(
        Boolean,
        default=True,
        index=True,
        comment="Is the job active"
    )
    last_run_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="When the job last ran"
    )
    next_run_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="When the job will run next"
    )
    last_status = Column(
        Enum(JobStatus, name="job_status_enum"),
        nullable=True,
        index=True,
        comment="Status of last execution"
    )
    run_count = Column(
        Integer,
        default=0,
        comment="Total number of executions"
    )
    success_count = Column(
        Integer,
        default=0,
        comment="Number of successful executions"
    )
    failure_count = Column(
        Integer,
        default=0,
        comment="Number of failed executions"
    )
    config = Column(
        JSONB,
        nullable=False,
        default={},
        comment="Job configuration and parameters"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the job was created"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When the job was last updated"
    )

    def __repr__(self) -> str:
        return f"<ScheduledJob(id={self.id}, name={self.name}, type={self.job_type}, active={self.is_active})>"
