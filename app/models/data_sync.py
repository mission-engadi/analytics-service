"""DataSync database model.

Tracks data synchronization from other services.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ServiceName(str, enum.Enum):
    """Enum for service names in the platform."""
    AUTH = "auth"
    CONTENT = "content"
    PARTNERS_CRM = "partners_crm"
    PROJECTS = "projects"
    SOCIAL_MEDIA = "social_media"
    NOTIFICATION = "notification"


class SyncType(str, enum.Enum):
    """Enum for synchronization types."""
    FULL = "full"
    INCREMENTAL = "incremental"
    MANUAL = "manual"


class SyncStatus(str, enum.Enum):
    """Enum for synchronization status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSync(Base):
    """DataSync model for tracking data synchronization.
    
    This model tracks synchronization of data from other services:
    - Auth service user data
    - Content service content metrics
    - Partners CRM partner data
    - Projects service project data
    - Social Media service post metrics
    - Notification service notification metrics
    
    Attributes:
        id: Unique identifier (UUID)
        service_name: Service being synchronized
        sync_type: Type of synchronization (full, incremental, manual)
        status: Current status of synchronization
        started_at: When synchronization started
        completed_at: When synchronization completed
        records_processed: Number of records processed
        records_failed: Number of records that failed
        last_sync_timestamp: Timestamp of last successful sync
        error_message: Error message if synchronization failed
        meta: Additional metadata as JSONB
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "data_syncs"
    
    # Override id to use UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    service_name: Mapped[ServiceName] = mapped_column(
        Enum(ServiceName, name="data_sync_service_name_enum"),
        nullable=False,
        index=True,
        comment="Service being synchronized"
    )
    
    sync_type: Mapped[SyncType] = mapped_column(
        Enum(SyncType, name="sync_type_enum"),
        nullable=False,
        index=True,
        comment="Type of synchronization"
    )
    
    status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus, name="sync_status_enum"),
        nullable=False,
        default=SyncStatus.PENDING,
        index=True,
        comment="Current status of synchronization"
    )
    
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When synchronization started"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When synchronization completed"
    )
    
    records_processed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of records processed"
    )
    
    records_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of records that failed"
    )
    
    last_sync_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of last successful sync"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if synchronization failed"
    )
    
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional metadata"
    )
    
    def __repr__(self) -> str:
        return (
            f"<DataSync(id={self.id}, service={self.service_name.value}, "
            f"type={self.sync_type.value}, status={self.status.value}, "
            f"processed={self.records_processed}, failed={self.records_failed})>"
        )
