"""Dashboard database model.

Stores dashboard configurations for different user types and use cases.
"""

import enum
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import String, Boolean, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class DashboardType(str, enum.Enum):
    """Enum for different types of dashboards."""
    EXECUTIVE = "executive"
    PARTNER = "partner"
    PROJECT = "project"
    SOCIAL_MEDIA = "social_media"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class Dashboard(Base):
    """Dashboard model for storing dashboard configurations.
    
    This model stores dashboard configurations including:
    - Dashboard name and description
    - Dashboard type (executive, partner, project, etc.)
    - Dashboard configuration (widgets, layout, filters)
    - Visibility settings (public, private)
    - Default dashboard flag
    
    Attributes:
        id: Unique identifier (UUID)
        name: Dashboard name
        dashboard_type: Type of dashboard
        description: Dashboard description
        config: Dashboard configuration as JSONB (widgets, layout, filters)
        is_default: Whether this is the default dashboard for its type
        is_public: Whether the dashboard is publicly accessible
        created_by: User ID who created the dashboard (UUID)
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "dashboards"
    
    # Override id to use UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Dashboard name"
    )
    
    dashboard_type: Mapped[DashboardType] = mapped_column(
        Enum(DashboardType, name="dashboard_type_enum"),
        nullable=False,
        index=True,
        comment="Type of dashboard"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Dashboard description"
    )
    
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dashboard configuration (widgets, layout, filters)"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether this is the default dashboard for its type"
    )
    
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the dashboard is publicly accessible"
    )
    
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User ID who created the dashboard"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Dashboard(id={self.id}, name='{self.name}', "
            f"type={self.dashboard_type.value}, is_default={self.is_default}, "
            f"is_public={self.is_public})>"
        )
