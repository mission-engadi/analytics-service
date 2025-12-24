"""API endpoints for goal tracking."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.goal import GoalMetricType, GoalStatus
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalProgressUpdate,
    GoalResponse,
    GoalProgressResponse,
    GoalForecastResponse,
)
from app.services.goal_service import GoalService

router = APIRouter()


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new KPI goal.
    
    - **name**: Goal name
    - **metric_type**: Type of metric to track
    - **target_value**: Target value to achieve
    - **start_date**: Goal start date
    - **end_date**: Goal end date
    - **alert_threshold**: Optional alert threshold percentage
    """
    service = GoalService(db)
    goal = await service.create_goal(goal_data)
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a goal by ID.
    """
    service = GoalService(db)
    goal = await service.get_goal(goal_id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    return goal


@router.get("", response_model=List[GoalResponse])
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    metric_type: Optional[GoalMetricType] = None,
    status_filter: Optional[GoalStatus] = Query(None, alias="status"),
    created_by: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List goals with optional filters.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **metric_type**: Filter by metric type
    - **status**: Filter by goal status
    - **created_by**: Filter by creator user ID
    """
    service = GoalService(db)
    goals = await service.list_goals(
        skip=skip,
        limit=limit,
        metric_type=metric_type,
        status=status_filter,
        created_by=created_by,
    )
    return goals


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a goal.
    """
    service = GoalService(db)
    goal = await service.update_goal(goal_id, goal_data)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a goal.
    """
    service = GoalService(db)
    deleted = await service.delete_goal(goal_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    return None


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed progress information for a goal.
    
    Returns:
    - Current progress percentage
    - Days remaining
    - Daily required progress
    - On-track status
    - Forecast value
    """
    service = GoalService(db)
    progress = await service.get_progress(goal_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    return progress


@router.post("/{goal_id}/update-progress", response_model=GoalResponse)
async def update_goal_progress(
    goal_id: UUID,
    progress_data: GoalProgressUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update goal progress with new current value.
    
    Automatically:
    - Recalculates progress percentage
    - Updates goal status
    - Triggers alerts if threshold reached
    - Updates forecast
    """
    service = GoalService(db)
    goal = await service.update_progress(goal_id, progress_data)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    return goal


@router.get("/forecast/all", response_model=List[GoalForecastResponse])
async def get_goal_forecasts(
    metric_type: Optional[GoalMetricType] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get forecasts for all active goals.
    
    - **metric_type**: Optional filter by metric type
    
    Returns:
    - Forecasted final values
    - Likelihood of achievement
    - Projected completion dates
    - Recommended actions
    """
    service = GoalService(db)
    forecasts = await service.get_forecasts(metric_type=metric_type)
    return forecasts
