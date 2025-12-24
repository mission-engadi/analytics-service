"""
Notification Analytics API Endpoints.

Provides REST API for notification analytics.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.notification_analytics_service import NotificationAnalyticsService

router = APIRouter()


@router.get(
    "/statistics",
    summary="Get notification statistics"
)
async def get_notification_statistics(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification statistics including delivery rates.
    """
    statistics = await NotificationAnalyticsService.get_notification_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return statistics


@router.get(
    "/delivery",
    summary="Get delivery rates"
)
async def get_delivery_rates(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification delivery rates over time.
    """
    rates = await NotificationAnalyticsService.get_delivery_rates(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return rates


@router.get(
    "/channels",
    summary="Get channel effectiveness"
)
async def get_channel_effectiveness(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification channel effectiveness.
    """
    effectiveness = await NotificationAnalyticsService.get_channel_effectiveness(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return effectiveness
