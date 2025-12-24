"""
Dashboard Service - Business logic for dashboard operations.

Handles CRUD operations and data fetching for dashboards.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import Dashboard, DashboardType
from app.schemas.dashboard import DashboardCreate, DashboardUpdate
from app.services.metric_service import MetricService


class DashboardService:
    """Service for dashboard operations."""
    
    @staticmethod
    async def create_dashboard(
        db: AsyncSession,
        dashboard_data: DashboardCreate
    ) -> Dashboard:
        """
        Create a new dashboard.
        
        Args:
            db: Database session
            dashboard_data: Dashboard creation data
            
        Returns:
            Created dashboard
        """
        dashboard = Dashboard(**dashboard_data.model_dump())
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        return dashboard
    
    @staticmethod
    async def get_dashboard(
        db: AsyncSession,
        dashboard_id: UUID
    ) -> Optional[Dashboard]:
        """
        Get dashboard by ID.
        
        Args:
            db: Database session
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard if found, None otherwise
        """
        result = await db.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_dashboards(
        db: AsyncSession,
        dashboard_type: Optional[DashboardType] = None,
        is_default: Optional[bool] = None,
        is_public: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dashboard]:
        """
        List dashboards with filters.
        
        Args:
            db: Database session
            dashboard_type: Filter by type
            is_default: Filter by default flag
            is_public: Filter by public flag
            created_by: Filter by creator
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of dashboards
        """
        query = select(Dashboard)
        
        conditions = []
        if dashboard_type:
            conditions.append(Dashboard.dashboard_type == dashboard_type)
        if is_default is not None:
            conditions.append(Dashboard.is_default == is_default)
        if is_public is not None:
            conditions.append(Dashboard.is_public == is_public)
        if created_by:
            conditions.append(Dashboard.created_by == created_by)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(Dashboard.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_dashboard(
        db: AsyncSession,
        dashboard_id: UUID,
        dashboard_data: DashboardUpdate
    ) -> Optional[Dashboard]:
        """
        Update dashboard.
        
        Args:
            db: Database session
            dashboard_id: Dashboard ID
            dashboard_data: Update data
            
        Returns:
            Updated dashboard if found, None otherwise
        """
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)
        if not dashboard:
            return None
        
        update_data = dashboard_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)
        
        await db.commit()
        await db.refresh(dashboard)
        return dashboard
    
    @staticmethod
    async def delete_dashboard(db: AsyncSession, dashboard_id: UUID) -> bool:
        """
        Delete dashboard.
        
        Args:
            db: Database session
            dashboard_id: Dashboard ID
            
        Returns:
            True if deleted, False if not found
        """
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)
        if not dashboard:
            return False
        
        await db.delete(dashboard)
        await db.commit()
        return True
    
    @staticmethod
    async def get_dashboard_data(
        db: AsyncSession,
        dashboard_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get dashboard with widget data.
        
        Args:
            db: Database session
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard data with widgets
        """
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)
        if not dashboard:
            return None
        
        # Return dashboard with config
        return {
            "id": str(dashboard.id),
            "name": dashboard.name,
            "dashboard_type": dashboard.dashboard_type,
            "description": dashboard.description,
            "config": dashboard.config,
            "is_default": dashboard.is_default,
            "is_public": dashboard.is_public,
            "created_at": dashboard.created_at.isoformat(),
            "updated_at": dashboard.updated_at.isoformat()
        }
    
    @staticmethod
    async def get_executive_dashboard(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get executive dashboard data.
        
        Args:
            db: Database session
            
        Returns:
            Executive dashboard data
        """
        # Get default executive dashboard
        result = await db.execute(
            select(Dashboard).where(
                and_(
                    Dashboard.dashboard_type == DashboardType.executive,
                    Dashboard.is_default == True
                )
            ).limit(1)
        )
        dashboard = result.scalar_one_or_none()
        
        if not dashboard:
            # Return empty executive dashboard
            return {
                "dashboard_type": "executive",
                "widgets": [],
                "message": "No executive dashboard configured"
            }
        
        return await DashboardService.get_dashboard_data(db, dashboard.id)
