"""
Data Sync API Endpoints.

Provides REST API for data synchronization operations.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services.data_sync_service import DataSyncService
from app.services.aggregation_service import AggregationService
from app.schemas.data_sync import DataSyncResponse
from app.models.data_sync import ServiceName, SyncType, SyncStatus

router = APIRouter()


@router.post(
    "",
    summary="Trigger manual sync"
)
async def trigger_sync(
    service_name: ServiceName,
    sync_type: SyncType = SyncType.manual,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger a manual data sync for a service.
    
    Requires authentication.
    """
    result = await AggregationService.trigger_sync(
        db=db,
        service_name=service_name,
        sync_type=sync_type
    )
    return result


@router.get(
    "/{sync_id}",
    response_model=DataSyncResponse,
    summary="Get sync record"
)
async def get_sync_record(
    sync_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> DataSyncResponse:
    """
    Get a sync record by ID.
    """
    sync_record = await DataSyncService.get_sync_record(db, sync_id)
    if not sync_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync record not found"
        )
    return DataSyncResponse.model_validate(sync_record)


@router.get(
    "",
    response_model=List[DataSyncResponse],
    summary="List sync records"
)
async def list_sync_records(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    sync_type: Optional[SyncType] = Query(None, description="Filter by sync type"),
    status: Optional[SyncStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db)
) -> List[DataSyncResponse]:
    """
    List sync records with optional filters.
    """
    sync_records = await DataSyncService.list_sync_records(
        db=db,
        service_name=service_name,
        sync_type=sync_type,
        status=status,
        skip=skip,
        limit=limit
    )
    return [DataSyncResponse.model_validate(s) for s in sync_records]


@router.get(
    "/status/current",
    summary="Get sync status"
)
async def get_sync_status(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current sync status.
    """
    status_data = await DataSyncService.get_sync_status(db, service_name)
    return status_data


@router.get(
    "/statistics/summary",
    summary="Get sync statistics"
)
async def get_sync_statistics(
    service_name: Optional[ServiceName] = Query(None, description="Filter by service"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sync statistics.
    
    Requires authentication.
    """
    statistics = await DataSyncService.get_sync_statistics(db, service_name)
    return statistics


@router.post(
    "/aggregate-all",
    summary="Aggregate all services"
)
async def aggregate_all_services(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger data aggregation from all services.
    
    Requires authentication.
    """
    result = await AggregationService.aggregate_all_services(db)
    return result
