"""
Project Analytics Service - Analytics for Projects data.

Integrates with Projects Service to provide analytics.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.service_client import ServiceClient, ServiceURLs
from app.services.metric_service import MetricService
from app.models.metric import ServiceName, MetricType

logger = logging.getLogger(__name__)


class ProjectAnalyticsService:
    """Service for project analytics."""
    
    @staticmethod
    async def get_project_statistics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Project statistics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Get metrics from database
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.projects,
            metric_type=MetricType.project,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        total_projects = len(set(m.dimensions.get("project_id") for m in metrics if m.dimensions.get("project_id")))
        active_projects = len([m for m in metrics if m.dimensions.get("status") == "active"])
        
        # Try to fetch from Projects Service
        try:
            async with ServiceClient() as client:
                url = ServiceURLs.projects_service("/api/v1/projects/statistics")
                params = {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                response = await client.get(url, params=params)
                
                return {
                    "total_projects": response.get("total_projects", total_projects),
                    "active_projects": response.get("active_projects", active_projects),
                    "completed_projects": response.get("completed_projects", 0),
                    "project_types": response.get("project_types", {}),
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to fetch from Projects Service: {e}")
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": 0,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "source": "local_metrics"
            }
    
    @staticmethod
    async def get_impact_metrics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get project impact metrics.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Impact metrics
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Get beneficiary metrics
        beneficiary_metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.projects,
            metric_type=MetricType.beneficiary,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        total_beneficiaries = sum(m.value for m in beneficiary_metrics)
        
        return {
            "total_beneficiaries": int(total_beneficiaries),
            "projects_with_impact": len(set(m.dimensions.get("project_id") for m in beneficiary_metrics if m.dimensions.get("project_id"))),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_completion_rates(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get project completion rates.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Completion rates
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Get project metrics
        metrics = await MetricService.list_metrics(
            db=db,
            service_name=ServiceName.projects,
            metric_type=MetricType.project,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Calculate completion rates
        total = len(metrics)
        completed = len([m for m in metrics if m.dimensions.get("status") == "completed"])
        in_progress = len([m for m in metrics if m.dimensions.get("status") == "in_progress"])
        
        return {
            "total_projects": total,
            "completed_projects": completed,
            "in_progress_projects": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_beneficiary_trends(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get beneficiary trends.
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Beneficiary trends
        """
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()
        
        # Get time-series data
        time_series = await MetricService.get_time_series(
            db=db,
            service_name=ServiceName.projects,
            metric_type=MetricType.beneficiary,
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
                "total_beneficiaries": sum(t["sum"] for t in time_series)
            }
        }
