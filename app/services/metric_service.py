"""
Metric Service - Business logic for metric operations.

Handles CRUD operations, aggregations, and analytics for metrics.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric, ServiceName, MetricType
from app.schemas.metric import MetricCreate, MetricUpdate, MetricAggregation


class MetricService:
    """Service for metric operations."""
    
    @staticmethod
    async def create_metric(
        db: AsyncSession,
        metric_data: MetricCreate
    ) -> Metric:
        """
        Create a new metric.
        
        Args:
            db: Database session
            metric_data: Metric creation data
            
        Returns:
            Created metric
        """
        metric = Metric(**metric_data.model_dump())
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        return metric
    
    @staticmethod
    async def get_metric(db: AsyncSession, metric_id: UUID) -> Optional[Metric]:
        """
        Get metric by ID.
        
        Args:
            db: Database session
            metric_id: Metric ID
            
        Returns:
            Metric if found, None otherwise
        """
        result = await db.execute(
            select(Metric).where(Metric.id == metric_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_metrics(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None,
        metric_type: Optional[MetricType] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Metric]:
        """
        List metrics with filters.
        
        Args:
            db: Database session
            service_name: Filter by service
            metric_type: Filter by type
            metric_name: Filter by name
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of metrics
        """
        query = select(Metric)
        
        conditions = []
        if service_name:
            conditions.append(Metric.service_name == service_name)
        if metric_type:
            conditions.append(Metric.metric_type == metric_type)
        if metric_name:
            conditions.append(Metric.metric_name == metric_name)
        if start_date:
            conditions.append(Metric.date >= start_date)
        if end_date:
            conditions.append(Metric.date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(Metric.timestamp)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def delete_metric(db: AsyncSession, metric_id: UUID) -> bool:
        """
        Delete metric.
        
        Args:
            db: Database session
            metric_id: Metric ID
            
        Returns:
            True if deleted, False if not found
        """
        metric = await MetricService.get_metric(db, metric_id)
        if not metric:
            return False
        
        await db.delete(metric)
        await db.commit()
        return True
    
    @staticmethod
    async def aggregate_metrics(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None,
        metric_type: Optional[MetricType] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = "date"
    ) -> List[MetricAggregation]:
        """
        Aggregate metrics with statistics.
        
        Args:
            db: Database session
            service_name: Filter by service
            metric_type: Filter by type
            metric_name: Filter by name
            start_date: Filter by start date
            end_date: Filter by end date
            group_by: Group by field (date, service_name, metric_type, metric_name)
            
        Returns:
            List of aggregated metrics
        """
        # Build base query conditions
        conditions = []
        if service_name:
            conditions.append(Metric.service_name == service_name)
        if metric_type:
            conditions.append(Metric.metric_type == metric_type)
        if metric_name:
            conditions.append(Metric.metric_name == metric_name)
        if start_date:
            conditions.append(Metric.date >= start_date)
        if end_date:
            conditions.append(Metric.date <= end_date)
        
        # Determine group by column
        group_column = getattr(Metric, group_by)
        
        # Build aggregation query
        query = select(
            group_column.label("group_key"),
            func.count(Metric.id).label("count"),
            func.sum(Metric.value).label("sum"),
            func.avg(Metric.value).label("avg"),
            func.min(Metric.value).label("min"),
            func.max(Metric.value).label("max")
        )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.group_by(group_column).order_by(group_column)
        
        result = await db.execute(query)
        rows = result.all()
        
        # Convert to MetricAggregation objects
        aggregations = []
        for row in rows:
            aggregations.append(
                MetricAggregation(
                    group_key=str(row.group_key),
                    count=row.count,
                    sum=float(row.sum) if row.sum else 0.0,
                    avg=float(row.avg) if row.avg else 0.0,
                    min=float(row.min) if row.min else 0.0,
                    max=float(row.max) if row.max else 0.0
                )
            )
        
        return aggregations
    
    @staticmethod
    async def get_metrics_by_service(
        db: AsyncSession,
        service_name: ServiceName,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics for a specific service.
        
        Args:
            db: Database session
            service_name: Service name
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum records
            
        Returns:
            List of metrics
        """
        return await MetricService.list_metrics(
            db=db,
            service_name=service_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    @staticmethod
    async def get_metrics_by_type(
        db: AsyncSession,
        metric_type: MetricType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics by type.
        
        Args:
            db: Database session
            metric_type: Metric type
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum records
            
        Returns:
            List of metrics
        """
        return await MetricService.list_metrics(
            db=db,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    @staticmethod
    async def get_time_series(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None,
        metric_type: Optional[MetricType] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Get time-series data for metrics.
        
        Args:
            db: Database session
            service_name: Filter by service
            metric_type: Filter by type
            metric_name: Filter by name
            start_date: Start date
            end_date: End date
            interval: Time interval (hourly, daily, weekly, monthly)
            
        Returns:
            Time-series data
        """
        # Use date aggregation for simplicity
        aggregations = await MetricService.aggregate_metrics(
            db=db,
            service_name=service_name,
            metric_type=metric_type,
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            group_by="date"
        )
        
        # Convert to time-series format
        time_series = []
        for agg in aggregations:
            time_series.append({
                "timestamp": agg.group_key,
                "count": agg.count,
                "sum": agg.sum,
                "avg": agg.avg,
                "min": agg.min,
                "max": agg.max
            })
        
        return time_series
