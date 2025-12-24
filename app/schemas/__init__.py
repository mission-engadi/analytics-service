"""Pydantic schemas for request/response validation."""

from app.schemas.example import (
    ExampleCreate,
    ExampleUpdate,
    ExampleResponse,
)  # noqa: F401

from app.schemas.metric import (
    MetricBase,
    MetricCreate,
    MetricUpdate,
    MetricResponse,
    MetricAggregation,
)  # noqa: F401

from app.schemas.dashboard import (
    DashboardBase,
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardWidgetData,
)  # noqa: F401

from app.schemas.data_sync import (
    DataSyncBase,
    DataSyncCreate,
    DataSyncUpdate,
    DataSyncResponse,
    DataSyncStats,
)  # noqa: F401

__all__ = [
    "ExampleCreate",
    "ExampleUpdate",
    "ExampleResponse",
    "MetricBase",
    "MetricCreate",
    "MetricUpdate",
    "MetricResponse",
    "MetricAggregation",
    "DashboardBase",
    "DashboardCreate",
    "DashboardUpdate",
    "DashboardResponse",
    "DashboardWidgetData",
    "DataSyncBase",
    "DataSyncCreate",
    "DataSyncUpdate",
    "DataSyncResponse",
    "DataSyncStats",
]
