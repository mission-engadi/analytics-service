"""
Partner Analytics Service - Analytics for Partners CRM data.

Integrates with Partners CRM Service to provide analytics.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.service_client import ServiceClient, ServiceURLs
from app.services.metric_service import MetricService
from app.models.metric import ServiceName, MetricType
from app.schemas.metric import MetricCreate

logger = logging.getLogger(__name__)


class PartnerAnalyticsService:
    """Service for partner analytics."""
    
    @staticmethod
    async def get_partner_statistics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get partner statistics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Partner statistics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get metrics from database
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.partner,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Calculate statistics
        total_partners = len(set(m.dimensions.get("partner_id") for m in metrics if m.dimensions.get("partner_id")))
        active_partners = len([m for m in metrics if m.dimensions.get("is_active")])
        
        # Try to fetch from Partners CRM Service
        try:
            async with ServiceClient() as client:
                url = ServiceURLs.partners_crm_service("/api/v1/partners/statistics")
                params = {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                response = await client.get(url, params=params)
                
                # Merge with local metrics
                return {
                    "total_partners": response.get("total_partners", total_partners),
                    "active_partners": response.get("active_partners", active_partners),
                    "new_partners": response.get("new_partners", 0),
                    "partner_types": response.get("partner_types", {}),
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to fetch from Partners CRM Service: {e}")
            # Return local metrics
            return {
                "total_partners": total_partners,
                "active_partners": active_partners,
                "new_partners": 0,
                "partner_types": {},
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "source": "local_metrics"
            }
    
    @staticmethod
    async def get_donation_trends(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get donation trends.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Donation trends
        """
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()
        
        # Get donation metrics
        aggregations = await MetricService.aggregate_metrics(
            db=db,
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.donation,
            start_date=start_date,
            end_date=end_date,
            group_by="date"
        )
        
        # Format trends
        trends = []
        for agg in aggregations:
            trends.append({
                "date": agg.group_key,
                "total_donations": agg.count,
                "total_amount": agg.sum,
                "average_amount": agg.avg,
                "min_amount": agg.min,
                "max_amount": agg.max
            })
        
        return {
            "trends": trends,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_donations": sum(t["total_donations"] for t in trends),
                "total_amount": sum(t["total_amount"] for t in trends)
            }
        }
    
    @staticmethod
    async def get_engagement_metrics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get partner engagement metrics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Engagement metrics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get engagement metrics
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.partners_crm,
            metric_type=MetricType.engagement,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Calculate engagement
        total_interactions = len(metrics)
        unique_partners = len(set(m.dimensions.get("partner_id") for m in metrics if m.dimensions.get("partner_id")))
        
        return {
            "total_interactions": total_interactions,
            "unique_partners": unique_partners,
            "average_interactions_per_partner": total_interactions / unique_partners if unique_partners > 0 else 0,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_partner_breakdown(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get partner type breakdown.
        
        Args:
            db: Database session
            
        Returns:
            Partner type breakdown
        """
        # Try to fetch from Partners CRM Service
        try:
            async with ServiceClient() as client:
                url = ServiceURLs.partners_crm_service("/api/v1/partners/breakdown")
                response = await client.get(url)
                return response
        except Exception as e:
            logger.warning(f"Failed to fetch from Partners CRM Service: {e}")
            return {
                "partner_types": [],
                "message": "Unable to fetch partner breakdown"
            }
