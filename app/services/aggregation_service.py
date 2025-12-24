"""
Aggregation Service - Orchestrates data aggregation from all services.

Handles sync jobs, error handling, and caching for aggregated data.
"""
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio

from app.core.service_client import ServiceClient, ServiceURLs
from app.core.config import settings
from app.services.data_sync_service import DataSyncService
from app.services.metric_service import MetricService
from app.models.data_sync import ServiceName, SyncType, SyncStatus
from app.models.metric import MetricType
from app.schemas.data_sync import DataSyncCreate, DataSyncUpdate
from app.schemas.metric import MetricCreate

logger = logging.getLogger(__name__)


class AggregationService:
    """Service for data aggregation orchestration."""
    
    @staticmethod
    async def trigger_sync(
        db: AsyncSession,
        service_name: ServiceName,
        sync_type: SyncType = SyncType.manual
    ) -> Dict[str, Any]:
        """
        Trigger data sync for a service.
        
        Args:
            db: Database session
            service_name: Service to sync
            sync_type: Type of sync (manual, incremental, full)
            
        Returns:
            Sync result
        """
        # Create sync record
        sync_data = DataSyncCreate(
            service_name=service_name,
            sync_type=sync_type,
            status=SyncStatus.pending,
            started_at=datetime.utcnow()
        )
        sync_record = await DataSyncService.create_sync_record(db, sync_data)
        
        try:
            # Update status to running
            await DataSyncService.update_sync_record(
                db,
                sync_record.id,
                DataSyncUpdate(status=SyncStatus.running)
            )
            
            # Perform sync based on service
            records_processed = 0
            records_failed = 0
            
            if service_name == ServiceName.partners_crm:
                result = await AggregationService._sync_partners_data(db)
                records_processed = result["processed"]
                records_failed = result["failed"]
            elif service_name == ServiceName.projects:
                result = await AggregationService._sync_projects_data(db)
                records_processed = result["processed"]
                records_failed = result["failed"]
            elif service_name == ServiceName.social_media:
                result = await AggregationService._sync_social_media_data(db)
                records_processed = result["processed"]
                records_failed = result["failed"]
            elif service_name == ServiceName.notification:
                result = await AggregationService._sync_notification_data(db)
                records_processed = result["processed"]
                records_failed = result["failed"]
            
            # Update sync record as completed
            await DataSyncService.update_sync_record(
                db,
                sync_record.id,
                DataSyncUpdate(
                    status=SyncStatus.completed,
                    completed_at=datetime.utcnow(),
                    records_processed=records_processed,
                    records_failed=records_failed
                )
            )
            
            return {
                "sync_id": str(sync_record.id),
                "service_name": service_name,
                "status": "completed",
                "records_processed": records_processed,
                "records_failed": records_failed
            }
            
        except Exception as e:
            logger.error(f"Sync failed for {service_name}: {e}", exc_info=True)
            
            # Update sync record as failed
            await DataSyncService.update_sync_record(
                db,
                sync_record.id,
                DataSyncUpdate(
                    status=SyncStatus.failed,
                    completed_at=datetime.utcnow(),
                    error_message=str(e)
                )
            )
            
            return {
                "sync_id": str(sync_record.id),
                "service_name": service_name,
                "status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    async def aggregate_all_services(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Aggregate data from all services.
        
        Args:
            db: Database session
            
        Returns:
            Aggregation results
        """
        services = [
            ServiceName.partners_crm,
            ServiceName.projects,
            ServiceName.social_media,
            ServiceName.notification
        ]
        
        results = []
        for service in services:
            result = await AggregationService.trigger_sync(
                db,
                service,
                SyncType.manual
            )
            results.append(result)
        
        # Calculate totals
        total_processed = sum(r.get("records_processed", 0) for r in results)
        total_failed = sum(r.get("records_failed", 0) for r in results)
        
        return {
            "services_synced": len(services),
            "total_records_processed": total_processed,
            "total_records_failed": total_failed,
            "results": results
        }
    
    @staticmethod
    async def _sync_partners_data(db: AsyncSession) -> Dict[str, int]:
        """Sync Partners CRM data."""
        processed = 0
        failed = 0
        
        try:
            async with ServiceClient(timeout=settings.SYNC_TIMEOUT_SECONDS) as client:
                # Fetch partner data
                url = ServiceURLs.partners_crm_service("/api/v1/partners")
                response = await client.get(url, params={"limit": settings.SYNC_BATCH_SIZE})
                
                partners = response.get("partners", [])
                for partner in partners:
                    try:
                        # Create metric for each partner
                        metric_data = MetricCreate(
                            service_name=ServiceName.partners_crm,
                            metric_type=MetricType.partner,
                            metric_name="partner_active",
                            value=1.0,
                            dimensions={
                                "partner_id": partner.get("id"),
                                "partner_type": partner.get("type"),
                                "is_active": partner.get("is_active", False)
                            },
                            timestamp=datetime.utcnow(),
                            date=datetime.utcnow().date()
                        )
                        await MetricService.create_metric(db, metric_data)
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process partner: {e}")
                        failed += 1
        except Exception as e:
            logger.error(f"Failed to sync partners data: {e}")
            failed += 1
        
        return {"processed": processed, "failed": failed}
    
    @staticmethod
    async def _sync_projects_data(db: AsyncSession) -> Dict[str, int]:
        """Sync Projects data."""
        processed = 0
        failed = 0
        
        try:
            async with ServiceClient(timeout=settings.SYNC_TIMEOUT_SECONDS) as client:
                # Fetch project data
                url = ServiceURLs.projects_service("/api/v1/projects")
                response = await client.get(url, params={"limit": settings.SYNC_BATCH_SIZE})
                
                projects = response.get("projects", [])
                for project in projects:
                    try:
                        # Create metric for each project
                        metric_data = MetricCreate(
                            service_name=ServiceName.projects,
                            metric_type=MetricType.project,
                            metric_name="project_status",
                            value=1.0,
                            dimensions={
                                "project_id": project.get("id"),
                                "project_type": project.get("type"),
                                "status": project.get("status")
                            },
                            timestamp=datetime.utcnow(),
                            date=datetime.utcnow().date()
                        )
                        await MetricService.create_metric(db, metric_data)
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process project: {e}")
                        failed += 1
        except Exception as e:
            logger.error(f"Failed to sync projects data: {e}")
            failed += 1
        
        return {"processed": processed, "failed": failed}
    
    @staticmethod
    async def _sync_social_media_data(db: AsyncSession) -> Dict[str, int]:
        """Sync Social Media data."""
        processed = 0
        failed = 0
        
        try:
            async with ServiceClient(timeout=settings.SYNC_TIMEOUT_SECONDS) as client:
                # Fetch social media posts
                url = ServiceURLs.social_media_service("/api/v1/posts")
                response = await client.get(url, params={"limit": settings.SYNC_BATCH_SIZE})
                
                posts = response.get("posts", [])
                for post in posts:
                    try:
                        # Create metric for each post
                        metric_data = MetricCreate(
                            service_name=ServiceName.social_media,
                            metric_type=MetricType.social_post,
                            metric_name="post_engagement",
                            value=float(post.get("engagement", 0)),
                            dimensions={
                                "post_id": post.get("id"),
                                "platform": post.get("platform"),
                                "post_type": post.get("type")
                            },
                            timestamp=datetime.utcnow(),
                            date=datetime.utcnow().date()
                        )
                        await MetricService.create_metric(db, metric_data)
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process post: {e}")
                        failed += 1
        except Exception as e:
            logger.error(f"Failed to sync social media data: {e}")
            failed += 1
        
        return {"processed": processed, "failed": failed}
    
    @staticmethod
    async def _sync_notification_data(db: AsyncSession) -> Dict[str, int]:
        """Sync Notification data."""
        processed = 0
        failed = 0
        
        try:
            async with ServiceClient(timeout=settings.SYNC_TIMEOUT_SECONDS) as client:
                # Fetch notification data
                url = ServiceURLs.notification_service("/api/v1/notifications")
                response = await client.get(url, params={"limit": settings.SYNC_BATCH_SIZE})
                
                notifications = response.get("notifications", [])
                for notification in notifications:
                    try:
                        # Create metric for each notification
                        metric_data = MetricCreate(
                            service_name=ServiceName.notification,
                            metric_type=MetricType.notification,
                            metric_name="notification_delivery",
                            value=1.0,
                            dimensions={
                                "notification_id": notification.get("id"),
                                "channel": notification.get("channel"),
                                "status": notification.get("status")
                            },
                            timestamp=datetime.utcnow(),
                            date=datetime.utcnow().date()
                        )
                        await MetricService.create_metric(db, metric_data)
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process notification: {e}")
                        failed += 1
        except Exception as e:
            logger.error(f"Failed to sync notification data: {e}")
            failed += 1
        
        return {"processed": processed, "failed": failed}
