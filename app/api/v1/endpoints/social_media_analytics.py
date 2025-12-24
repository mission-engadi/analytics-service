"""
Social Media Analytics API Endpoints.

Provides REST API for social media analytics.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.social_media_analytics_service import SocialMediaAnalyticsService

router = APIRouter()


@router.get(
    "/performance",
    summary="Get performance metrics"
)
async def get_performance_metrics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get social media performance metrics.
    """
    metrics = await SocialMediaAnalyticsService.get_performance_metrics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return metrics


@router.get(
    "/platforms",
    summary="Get platform comparison"
)
async def get_platform_comparison(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comparison of performance across platforms.
    """
    comparison = await SocialMediaAnalyticsService.get_platform_comparison(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return comparison


@router.get(
    "/engagement",
    summary="Get engagement trends"
)
async def get_engagement_trends(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get engagement trends over time.
    """
    trends = await SocialMediaAnalyticsService.get_engagement_trends(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return trends
