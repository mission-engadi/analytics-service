"""
Metrics API Endpoints.

Provides REST API for metric operations.
"""
from typing import List, Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services.metric_service import MetricService
from app.schemas.metric import (
    MetricCreate,
    MetricResponse,
    MetricAggregation
)
from app.models.metric import ServiceName, MetricType

router = APIRouter()


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create metric"
)
async def create_metric(
    metric_data: MetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MetricResponse:
    """
    Create a new metric.
    
    Requires authentication.
    """
    metric = await MetricService.create_metric(db, metric_data)
    return MetricResponse.model_validate(metric)


@router.get(
    "/{metric_id}",
    response_model=MetricResponse,
    summary="Get metric by ID"
)
async def get_metric(
    metric_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> MetricResponse:
    """
    Get a metric by ID.
    """
    metric = await MetricService.get_metric(db, metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    return MetricResponse.model_validate(metric)


@router.get(
    "",
    response_model=List[MetricResponse],
    summary="List metrics"
)
async def list_metrics(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    metric_type: Optional[MetricType] = Query(None, description="Filter by type"),
    metric_name: Optional[str] = Query(None, description="Filter by name"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db)
) -> List[MetricResponse]:
    """
    List metrics with optional filters.
    """
    metrics = await MetricService.list_metrics(
        db=db,
        service_name=service_name,
        metric_type=metric_type,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return [MetricResponse.model_validate(m) for m in metrics]


@router.delete(
    "/{metric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete metric"
)
async def delete_metric(
    metric_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete a metric.
    
    Requires authentication.
    """
    deleted = await MetricService.delete_metric(db, metric_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )


@router.get(
    "/aggregate/statistics",
    response_model=List[MetricAggregation],
    summary="Aggregate metrics"
)
async def aggregate_metrics(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    metric_type: Optional[MetricType] = Query(None, description="Filter by type"),
    metric_name: Optional[str] = Query(None, description="Filter by name"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    group_by: str = Query("date", description="Group by field"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[MetricAggregation]:
    """
    Get aggregated metric statistics.
    
    Requires authentication.
    """
    aggregations = await MetricService.aggregate_metrics(
        db=db,
        service_name=service_name,
        metric_type=metric_type,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )
    return aggregations


@router.get(
    "/by-service/{service_name}",
    response_model=List[MetricResponse],
    summary="Get metrics by service"
)
async def get_metrics_by_service(
    service_name: ServiceName,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records"),
    db: AsyncSession = Depends(get_db)
) -> List[MetricResponse]:
    """
    Get metrics for a specific service.
    """
    metrics = await MetricService.get_metrics_by_service(
        db=db,
        service_name=service_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return [MetricResponse.model_validate(m) for m in metrics]


@router.get(
    "/by-type/{metric_type}",
    response_model=List[MetricResponse],
    summary="Get metrics by type"
)
async def get_metrics_by_type(
    metric_type: MetricType,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records"),
    db: AsyncSession = Depends(get_db)
) -> List[MetricResponse]:
    """
    Get metrics by type.
    """
    metrics = await MetricService.get_metrics_by_type(
        db=db,
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return [MetricResponse.model_validate(m) for m in metrics]


@router.get(
    "/time-series/data",
    summary="Get time-series data"
)
async def get_time_series(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    metric_type: Optional[MetricType] = Query(None, description="Filter by type"),
    metric_name: Optional[str] = Query(None, description="Filter by name"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    interval: str = Query("daily", description="Time interval"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get time-series data for metrics.
    """
    time_series = await MetricService.get_time_series(
        db=db,
        service_name=service_name,
        metric_type=metric_type,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    return {"time_series": time_series}
