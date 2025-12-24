"""Metric database model.

Stores analytics metrics from all services in the platform.
"""

import enum
import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any

from sqlalchemy import String, Float, Enum, DateTime, Date, Index, Text
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


class MetricType(str, enum.Enum):
    """Enum for different types of metrics."""
    DONATION = "donation"
    PARTNER = "partner"
    PROJECT = "project"
    BENEFICIARY = "beneficiary"
    SOCIAL_POST = "social_post"
    NOTIFICATION = "notification"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    REVENUE = "revenue"


class Metric(Base):
    """Metric model for storing analytics data.
    
    This model stores metrics from all services including:
    - Donation metrics (amount, frequency, etc.)
    - Partner metrics (count, engagement, etc.)
    - Project metrics (progress, impact, etc.)
    - Social media metrics (posts, engagement, reach)
    - Notification metrics (sent, opened, clicked)
    - Engagement and conversion metrics
    
    Attributes:
        id: Unique identifier (UUID)
        service_name: Service that generated the metric
        metric_type: Type of metric (donation, partner, etc.)
        metric_name: Name of the metric (e.g., "total_donations", "new_partners")
        metric_value: Numeric value of the metric
        metric_unit: Unit of measurement (USD, count, percentage, etc.)
        dimensions: Additional dimensions as JSONB (partner_type, project_type, channel)
        timestamp: Timestamp when metric was recorded
        date: Date for daily aggregations
        meta: Additional context as JSONB
        created_at: Record creation timestamp
    """
    
    __tablename__ = "metrics"
    
    # Override id to use UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    service_name: Mapped[ServiceName] = mapped_column(
        Enum(ServiceName, name="service_name_enum"),
        nullable=False,
        index=True,
        comment="Service that generated the metric"
    )
    
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, name="metric_type_enum"),
        nullable=False,
        index=True,
        comment="Type of metric"
    )
    
    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of the metric"
    )
    
    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Numeric value of the metric"
    )
    
    metric_unit: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Unit of measurement (USD, count, percentage, etc.)"
    )
    
    dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional dimensions (partner_type, project_type, channel, etc.)"
    )
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp when metric was recorded"
    )
    
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date for daily aggregations"
    )
    
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional context"
    )
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index(
            "idx_metrics_service_type_date",
            "service_name",
            "metric_type",
            "date"
        ),
        Index(
            "idx_metrics_name_date",
            "metric_name",
            "date"
        ),
        Index(
            "idx_metrics_timestamp",
            "timestamp"
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Metric(id={self.id}, service={self.service_name.value}, "
            f"type={self.metric_type.value}, name='{self.metric_name}', "
            f"value={self.metric_value}, date={self.date})>"
        )
