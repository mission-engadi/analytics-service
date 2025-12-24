"""
Data Sync Service - Business logic for data synchronization.

Handles CRUD operations and tracking for data sync jobs.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_sync import DataSync, ServiceName, SyncType, SyncStatus
from app.schemas.data_sync import DataSyncCreate, DataSyncUpdate


class DataSyncService:
    """Service for data synchronization operations."""
    
    @staticmethod
    async def create_sync_record(
        db: AsyncSession,
        sync_data: DataSyncCreate
    ) -> DataSync:
        """
        Create a new sync record.
        
        Args:
            db: Database session
            sync_data: Sync creation data
            
        Returns:
            Created sync record
        """
        sync = DataSync(**sync_data.model_dump())
        db.add(sync)
        await db.commit()
        await db.refresh(sync)
        return sync
    
    @staticmethod
    async def get_sync_record(
        db: AsyncSession,
        sync_id: UUID
    ) -> Optional[DataSync]:
        """
        Get sync record by ID.
        
        Args:
            db: Database session
            sync_id: Sync ID
            
        Returns:
            Sync record if found, None otherwise
        """
        result = await db.execute(
            select(DataSync).where(DataSync.id == sync_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_sync_records(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None,
        sync_type: Optional[SyncType] = None,
        status: Optional[SyncStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DataSync]:
        """
        List sync records with filters.
        
        Args:
            db: Database session
            service_name: Filter by service
            sync_type: Filter by sync type
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of sync records
        """
        query = select(DataSync)
        
        conditions = []
        if service_name:
            conditions.append(DataSync.service_name == service_name)
        if sync_type:
            conditions.append(DataSync.sync_type == sync_type)
        if status:
            conditions.append(DataSync.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(DataSync.started_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_sync_record(
        db: AsyncSession,
        sync_id: UUID,
        sync_data: DataSyncUpdate
    ) -> Optional[DataSync]:
        """
        Update sync record.
        
        Args:
            db: Database session
            sync_id: Sync ID
            sync_data: Update data
            
        Returns:
            Updated sync record if found, None otherwise
        """
        sync = await DataSyncService.get_sync_record(db, sync_id)
        if not sync:
            return None
        
        update_data = sync_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sync, field, value)
        
        await db.commit()
        await db.refresh(sync)
        return sync
    
    @staticmethod
    async def get_sync_status(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None
    ) -> Dict[str, Any]:
        """
        Get current sync status.
        
        Args:
            db: Database session
            service_name: Filter by service
            
        Returns:
            Sync status information
        """
        # Get latest sync for each service
        query = select(DataSync)
        
        if service_name:
            query = query.where(DataSync.service_name == service_name)
        
        query = query.order_by(desc(DataSync.started_at)).limit(10)
        
        result = await db.execute(query)
        syncs = result.scalars().all()
        
        status = {
            "latest_syncs": [
                {
                    "id": str(sync.id),
                    "service_name": sync.service_name,
                    "sync_type": sync.sync_type,
                    "status": sync.status,
                    "started_at": sync.started_at.isoformat(),
                    "completed_at": sync.completed_at.isoformat() if sync.completed_at else None,
                    "records_processed": sync.records_processed,
                    "records_failed": sync.records_failed
                }
                for sync in syncs
            ]
        }
        
        return status
    
    @staticmethod
    async def get_sync_statistics(
        db: AsyncSession,
        service_name: Optional[ServiceName] = None
    ) -> Dict[str, Any]:
        """
        Get sync statistics.
        
        Args:
            db: Database session
            service_name: Filter by service
            
        Returns:
            Sync statistics
        """
        # Build query for statistics
        query = select(
            func.count(DataSync.id).label("total_syncs"),
            func.sum(DataSync.records_processed).label("total_records_processed"),
            func.sum(DataSync.records_failed).label("total_records_failed"),
            func.count(DataSync.id).filter(DataSync.status == SyncStatus.completed).label("completed_syncs"),
            func.count(DataSync.id).filter(DataSync.status == SyncStatus.failed).label("failed_syncs"),
            func.count(DataSync.id).filter(DataSync.status == SyncStatus.running).label("running_syncs")
        )
        
        if service_name:
            query = query.where(DataSync.service_name == service_name)
        
        result = await db.execute(query)
        row = result.one()
        
        statistics = {
            "total_syncs": row.total_syncs or 0,
            "total_records_processed": row.total_records_processed or 0,
            "total_records_failed": row.total_records_failed or 0,
            "completed_syncs": row.completed_syncs or 0,
            "failed_syncs": row.failed_syncs or 0,
            "running_syncs": row.running_syncs or 0
        }
        
        return statistics
