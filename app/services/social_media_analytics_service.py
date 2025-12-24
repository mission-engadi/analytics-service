"""
Social Media Analytics Service - Analytics for social media data.

Integrates with Social Media Service to provide analytics.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.service_client import ServiceClient, ServiceURLs
from app.services.metric_service import MetricService
from app.models.metric import ServiceName, MetricType

logger = logging.getLogger(__name__)


class SocialMediaAnalyticsService:
    """Service for social media analytics."""
    
    @staticmethod
    async def get_performance_metrics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get social media performance metrics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Performance metrics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get post metrics
        post_metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.social_media,
            metric_type=MetricType.social_post,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Get engagement metrics
        engagement_metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.social_media,
            metric_type=MetricType.engagement,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        total_posts = len(post_metrics)
        total_engagement = sum(m.value for m in engagement_metrics)
        
        return {
            "total_posts": total_posts,
            "total_engagement": int(total_engagement),
            "average_engagement_per_post": total_engagement / total_posts if total_posts > 0 else 0,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_platform_comparison(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get platform comparison.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Platform comparison data
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get all social media metrics
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.social_media,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Group by platform
        platforms = {}
        for metric in metrics:
            platform = metric.dimensions.get("platform", "unknown")
            if platform not in platforms:
                platforms[platform] = {
                    "platform": platform,
                    "posts": 0,
                    "engagement": 0
                }
            
            if metric.metric_type == MetricType.social_post:
                platforms[platform]["posts"] += 1
            elif metric.metric_type == MetricType.engagement:
                platforms[platform]["engagement"] += metric.value
        
        return {
            "platforms": list(platforms.values()),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_engagement_trends(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get engagement trends.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Engagement trends
        """
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()
        
        # Get time-series data
        time_series = await MetricService.get_time_series(
            db=db,
            service_name=ServiceName.social_media,
            metric_type=MetricType.engagement,
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
                "total_engagement": sum(t["sum"] for t in time_series),
                "average_daily_engagement": sum(t["avg"] for t in time_series) / len(time_series) if time_series else 0
            }
        }
