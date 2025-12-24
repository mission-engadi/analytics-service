"""
Dashboard API Endpoints.

Provides REST API for dashboard operations.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse
)
from app.models.dashboard import DashboardType

router = APIRouter()


@router.post(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dashboard"
)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> DashboardResponse:
    """
    Create a new dashboard.
    
    Requires authentication.
    """
    dashboard = await DashboardService.create_dashboard(db, dashboard_data)
    return DashboardResponse.model_validate(dashboard)


@router.get(
    "/{dashboard_id}",
    response_model=DashboardResponse,
    summary="Get dashboard by ID"
)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> DashboardResponse:
    """
    Get a dashboard by ID.
    """
    dashboard = await DashboardService.get_dashboard(db, dashboard_id)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    return DashboardResponse.model_validate(dashboard)


@router.get(
    "",
    response_model=List[DashboardResponse],
    summary="List dashboards"
)
async def list_dashboards(
    dashboard_type: Optional[DashboardType] = Query(None, description="Filter by type"),
    is_default: Optional[bool] = Query(None, description="Filter by default flag"),
    is_public: Optional[bool] = Query(None, description="Filter by public flag"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db)
) -> List[DashboardResponse]:
    """
    List dashboards with optional filters.
    """
    dashboards = await DashboardService.list_dashboards(
        db=db,
        dashboard_type=dashboard_type,
        is_default=is_default,
        is_public=is_public,
        skip=skip,
        limit=limit
    )
    return [DashboardResponse.model_validate(d) for d in dashboards]


@router.put(
    "/{dashboard_id}",
    response_model=DashboardResponse,
    summary="Update dashboard"
)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_data: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> DashboardResponse:
    """
    Update a dashboard.
    
    Requires authentication.
    """
    dashboard = await DashboardService.update_dashboard(db, dashboard_id, dashboard_data)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    return DashboardResponse.model_validate(dashboard)


@router.delete(
    "/{dashboard_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete dashboard"
)
async def delete_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete a dashboard.
    
    Requires authentication.
    """
    deleted = await DashboardService.delete_dashboard(db, dashboard_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )


@router.get(
    "/{dashboard_id}/data",
    summary="Get dashboard data"
)
async def get_dashboard_data(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard with widget data.
    """
    dashboard_data = await DashboardService.get_dashboard_data(db, dashboard_id)
    if not dashboard_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    return dashboard_data


@router.get(
    "/executive/default",
    summary="Get executive dashboard"
)
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """
    Get default executive dashboard.
    """
    dashboard_data = await DashboardService.get_executive_dashboard(db)
    return dashboard_data
