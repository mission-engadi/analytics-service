"""API router configuration.

This module aggregates all API routers for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    examples,
    health,
    metrics,
    dashboards,
    data_sync,
    partner_analytics,
    project_analytics,
    social_media_analytics,
    notification_analytics
)

api_router = APIRouter()

# Include all endpoint routers

# System endpoints
api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    examples.router,
    prefix="/examples",
    tags=["examples"],
)

# Metrics endpoints
api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["metrics"],
)

# Dashboard endpoints
api_router.include_router(
    dashboards.router,
    prefix="/dashboards",
    tags=["dashboards"],
)

# Data sync endpoints
api_router.include_router(
    data_sync.router,
    prefix="/sync",
    tags=["data-sync"],
)

# Analytics endpoints
api_router.include_router(
    partner_analytics.router,
    prefix="/analytics/partners",
    tags=["partner-analytics"],
)

api_router.include_router(
    project_analytics.router,
    prefix="/analytics/projects",
    tags=["project-analytics"],
)

api_router.include_router(
    social_media_analytics.router,
    prefix="/analytics/social-media",
    tags=["social-media-analytics"],
)

api_router.include_router(
    notification_analytics.router,
    prefix="/analytics/notifications",
    tags=["notification-analytics"],
)
