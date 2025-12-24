"""Goal model for tracking KPI goals and targets."""
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Enum, Boolean, Float, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base


class GoalMetricType(str, enum.Enum):
    """Types of metrics that can be tracked."""
    donation = "donation"
    partner = "partner"
    project = "project"
    beneficiary = "beneficiary"
    social_post = "social_post"
    notification = "notification"
    engagement = "engagement"
    conversion = "conversion"
    revenue = "revenue"


class GoalStatus(str, enum.Enum):
    """Goal achievement status."""
    active = "active"
    achieved = "achieved"
    failed = "failed"
    cancelled = "cancelled"


class Goal(Base):
    """Goal model for tracking KPI goals and progress.
    
    Stores goals with target values, current progress, and forecasting.
    Supports alerts when progress reaches thresholds.
    """
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Goal name")
    description = Column(Text, nullable=True, comment="Goal description")
    metric_type = Column(
        Enum(GoalMetricType, name="goal_metric_type_enum"),
        nullable=False,
        index=True,
        comment="Type of metric being tracked"
    )
    target_value = Column(
        Float,
        nullable=False,
        comment="Target value to achieve"
    )
    current_value = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Current progress value"
    )
    unit = Column(
        String(50),
        nullable=True,
        comment="Unit of measurement (USD, count, percentage, etc.)"
    )
    start_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Goal start date"
    )
    end_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Goal end date"
    )
    status = Column(
        Enum(GoalStatus, name="goal_status_enum"),
        nullable=False,
        default=GoalStatus.active,
        index=True,
        comment="Goal achievement status"
    )
    progress_percentage = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Progress as percentage"
    )
    alert_threshold = Column(
        Float,
        nullable=True,
        comment="Alert when progress reaches this percentage"
    )
    alert_sent = Column(
        Boolean,
        default=False,
        comment="Has alert been sent"
    )
    forecast_value = Column(
        Float,
        nullable=True,
        comment="Predicted final value based on current trend"
    )
    forecast_updated_at = Column(
        DateTime,
        nullable=True,
        comment="When the forecast was last updated"
    )
    created_by = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who created the goal"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the goal was created"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When the goal was last updated"
    )

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, name={self.name}, type={self.metric_type}, status={self.status}, progress={self.progress_percentage}%)>"
