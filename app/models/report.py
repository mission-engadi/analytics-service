"""Report model for generated analytics reports."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Boolean, Integer, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db.base_class import Base


class ReportType(str, enum.Enum):
    """Types of reports."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    annual = "annual"
    custom = "custom"


class ReportFormat(str, enum.Enum):
    """Report file formats."""
    pdf = "pdf"
    excel = "excel"
    csv = "csv"
    json = "json"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    pending = "pending"
    generating = "generating"
    completed = "completed"
    failed = "failed"


class Report(Base):
    """Report model for storing analytics reports.
    
    Stores metadata about generated reports including configuration,
    generation status, file paths, and scheduling information.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Report name")
    report_type = Column(
        Enum(ReportType, name="report_type_enum"),
        nullable=False,
        index=True,
        comment="Type of report"
    )
    format = Column(
        Enum(ReportFormat, name="report_format_enum"),
        nullable=False,
        index=True,
        comment="Report file format"
    )
    status = Column(
        Enum(ReportStatus, name="report_status_enum"),
        nullable=False,
        default=ReportStatus.pending,
        index=True,
        comment="Report generation status"
    )
    parameters = Column(
        JSONB,
        nullable=False,
        default={},
        comment="Report parameters (date range, filters, etc.)"
    )
    file_path = Column(
        String(500),
        nullable=True,
        comment="Path to generated report file"
    )
    file_size = Column(
        Integer,
        nullable=True,
        comment="File size in bytes"
    )
    generated_at = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="When the report was generated"
    )
    scheduled = Column(
        Boolean,
        default=False,
        index=True,
        comment="Is this a scheduled report"
    )
    schedule_config = Column(
        JSONB,
        nullable=True,
        comment="Cron schedule configuration if scheduled"
    )
    email_recipients = Column(
        ARRAY(String),
        nullable=True,
        comment="Email addresses to send report to"
    )
    created_by = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who created the report"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the report was created"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When the report was last updated"
    )

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, name={self.name}, type={self.report_type}, status={self.status})>"
