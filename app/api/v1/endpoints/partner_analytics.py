"""
Partner Analytics API Endpoints.

Provides REST API for partner analytics.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.partner_analytics_service import PartnerAnalyticsService

router = APIRouter()


@router.get(
    "/statistics",
    summary="Get partner statistics"
)
async def get_partner_statistics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get partner statistics including total partners, active partners, etc.
    """
    statistics = await PartnerAnalyticsService.get_partner_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return statistics


@router.get(
    "/donations",
    summary="Get donation trends"
)
async def get_donation_trends(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get donation trends and statistics.
    """
    trends = await PartnerAnalyticsService.get_donation_trends(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return trends


@router.get(
    "/engagement",
    summary="Get engagement metrics"
)
async def get_engagement_metrics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get partner engagement metrics.
    """
    metrics = await PartnerAnalyticsService.get_engagement_metrics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return metrics


@router.get(
    "/breakdown",
    summary="Get partner type breakdown"
)
async def get_partner_breakdown(
    db: AsyncSession = Depends(get_db)
):
    """
    Get breakdown of partners by type.
    """
    breakdown = await PartnerAnalyticsService.get_partner_breakdown(db)
    return breakdown
