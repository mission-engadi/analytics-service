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

from app.schemas.report import (
    ReportBase,
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportScheduleCreate,
    ReportEmailRequest,
)  # noqa: F401

from app.schemas.goal import (
    GoalBase,
    GoalCreate,
    GoalUpdate,
    GoalProgressUpdate,
    GoalResponse,
    GoalProgressResponse,
    GoalForecastResponse,
)  # noqa: F401

from app.schemas.scheduled_job import (
    ScheduledJobBase,
    ScheduledJobCreate,
    ScheduledJobUpdate,
    ScheduledJobResponse,
    ScheduledJobStats,
    JobTriggerRequest,
)  # noqa: F401

from app.schemas.advanced_analytics import (
    PredictionRequest,
    PredictionResponse,
    ForecastRequest,
    ForecastResponse,
    ComparisonRequest,
    ComparisonResponse,
    CustomCalculationRequest,
    CustomCalculationResponse,
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
    "ReportBase",
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportScheduleCreate",
    "ReportEmailRequest",
    "GoalBase",
    "GoalCreate",
    "GoalUpdate",
    "GoalProgressUpdate",
    "GoalResponse",
    "GoalProgressResponse",
    "GoalForecastResponse",
    "ScheduledJobBase",
    "ScheduledJobCreate",
    "ScheduledJobUpdate",
    "ScheduledJobResponse",
    "ScheduledJobStats",
    "JobTriggerRequest",
    "PredictionRequest",
    "PredictionResponse",
    "ForecastRequest",
    "ForecastResponse",
    "ComparisonRequest",
    "ComparisonResponse",
    "CustomCalculationRequest",
    "CustomCalculationResponse",
]
