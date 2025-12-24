"""
Notification Analytics Service - Analytics for notification data.

Integrates with Notification Service to provide analytics.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.service_client import ServiceClient, ServiceURLs
from app.services.metric_service import MetricService
from app.models.metric import ServiceName, MetricType

logger = logging.getLogger(__name__)


class NotificationAnalyticsService:
    """Service for notification analytics."""
    
    @staticmethod
    async def get_notification_statistics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get notification statistics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Notification statistics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get notification metrics
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.notification,
            metric_type=MetricType.notification,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        total_notifications = len(metrics)
        delivered = len([m for m in metrics if m.dimensions.get("status") == "delivered"])
        failed = len([m for m in metrics if m.dimensions.get("status") == "failed"])
        
        return {
            "total_notifications": total_notifications,
            "delivered_notifications": delivered,
            "failed_notifications": failed,
            "delivery_rate": (delivered / total_notifications * 100) if total_notifications > 0 else 0,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_delivery_rates(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get notification delivery rates.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Delivery rates
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get time-series data
        time_series = await MetricService.get_time_series(
            db=db,
            service_name=ServiceName.notification,
            metric_type=MetricType.notification,
            start_date=start_date,
            end_date=end_date,
            interval="daily"
        )
        
        return {
            "trends": time_series,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_notifications": sum(t["count"] for t in time_series)
            }
        }
    
    @staticmethod
    async def get_channel_effectiveness(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get notification channel effectiveness.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Channel effectiveness
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get all notification metrics
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.notification,
            metric_type=MetricType.notification,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Group by channel
        channels = {}
        for metric in metrics:
            channel = metric.dimensions.get("channel", "unknown")
            if channel not in channels:
                channels[channel] = {
                    "channel": channel,
                    "total": 0,
                    "delivered": 0,
                    "failed": 0
                }
            
            channels[channel]["total"] += 1
            status = metric.dimensions.get("status")
            if status == "delivered":
                channels[channel]["delivered"] += 1
            elif status == "failed":
                channels[channel]["failed"] += 1
        
        # Calculate delivery rates
        for channel_data in channels.values():
            total = channel_data["total"]
            channel_data["delivery_rate"] = (channel_data["delivered"] / total * 100) if total > 0 else 0
        
        return {
            "channels": list(channels.values()),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
