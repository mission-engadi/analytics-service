"""
Project Analytics API Endpoints.

Provides REST API for project analytics.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.project_analytics_service import ProjectAnalyticsService

router = APIRouter()


@router.get(
    "/statistics",
    summary="Get project statistics"
)
async def get_project_statistics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project statistics including total projects, active projects, etc.
    """
    statistics = await ProjectAnalyticsService.get_project_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return statistics


@router.get(
    "/impact",
    summary="Get impact metrics"
)
async def get_impact_metrics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project impact metrics including beneficiaries.
    """
    metrics = await ProjectAnalyticsService.get_impact_metrics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return metrics


@router.get(
    "/completion",
    summary="Get completion rates"
)
async def get_completion_rates(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project completion rates.
    """
    rates = await ProjectAnalyticsService.get_completion_rates(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return rates


@router.get(
    "/beneficiaries",
    summary="Get beneficiary trends"
)
async def get_beneficiary_trends(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get beneficiary trends over time.
    """
    trends = await ProjectAnalyticsService.get_beneficiary_trends(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return trends
