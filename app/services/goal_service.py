"""Service layer for goal tracking operations."""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.goal import Goal, GoalMetricType, GoalStatus
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalProgressUpdate,
    GoalProgressResponse,
    GoalForecastResponse,
)


class GoalService:
    """Service for managing KPI goals and tracking progress."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_goal(self, goal_data: GoalCreate) -> Goal:
        """Create a new goal."""
        goal = Goal(
            name=goal_data.name,
            description=goal_data.description,
            metric_type=goal_data.metric_type,
            target_value=goal_data.target_value,
            current_value=goal_data.current_value or 0.0,
            unit=goal_data.unit,
            start_date=goal_data.start_date,
            end_date=goal_data.end_date,
            alert_threshold=goal_data.alert_threshold,
            status=GoalStatus.active,
            progress_percentage=0.0,
            created_by=goal_data.created_by,
        )
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def get_goal(self, goal_id: UUID) -> Optional[Goal]:
        """Get a goal by ID."""
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id)
        )
        return result.scalar_one_or_none()

    async def list_goals(
        self,
        skip: int = 0,
        limit: int = 100,
        metric_type: Optional[GoalMetricType] = None,
        status: Optional[GoalStatus] = None,
        created_by: Optional[UUID] = None,
    ) -> List[Goal]:
        """List goals with filters."""
        query = select(Goal)
        filters = []

        if metric_type:
            filters.append(Goal.metric_type == metric_type)
        if status:
            filters.append(Goal.status == status)
        if created_by:
            filters.append(Goal.created_by == created_by)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Goal.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_goal(self, goal_id: UUID, goal_data: GoalUpdate) -> Optional[Goal]:
        """Update a goal."""
        goal = await self.get_goal(goal_id)
        if not goal:
            return None

        update_data = goal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def delete_goal(self, goal_id: UUID) -> bool:
        """Delete a goal."""
        goal = await self.get_goal(goal_id)
        if not goal:
            return False

        await self.db.delete(goal)
        await self.db.commit()
        return True

    async def update_progress(self, goal_id: UUID, progress_data: GoalProgressUpdate) -> Optional[Goal]:
        """Update goal progress and recalculate metrics."""
        goal = await self.get_goal(goal_id)
        if not goal:
            return None

        goal.current_value = progress_data.current_value
        goal.progress_percentage = (goal.current_value / goal.target_value) * 100

        # Update status based on progress
        if goal.progress_percentage >= 100:
            goal.status = GoalStatus.achieved
        elif date.today() > goal.end_date and goal.progress_percentage < 100:
            goal.status = GoalStatus.failed
        else:
            goal.status = GoalStatus.active

        # Check alert threshold
        if (
            goal.alert_threshold
            and not goal.alert_sent
            and goal.progress_percentage >= goal.alert_threshold
        ):
            goal.alert_sent = True
            # In production, send actual alert notification
            print(f"Alert: Goal '{goal.name}' reached {goal.progress_percentage}% progress")

        # Update forecast
        goal.forecast_value = await self._calculate_forecast(goal)
        goal.forecast_updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def get_progress(self, goal_id: UUID) -> Optional[GoalProgressResponse]:
        """Get detailed progress information for a goal."""
        goal = await self.get_goal(goal_id)
        if not goal:
            return None

        today = date.today()
        days_remaining = (goal.end_date - today).days
        remaining_value = goal.target_value - goal.current_value
        daily_required = remaining_value / days_remaining if days_remaining > 0 else 0

        # Check if on track
        total_days = (goal.end_date - goal.start_date).days
        expected_progress = ((today - goal.start_date).days / total_days) * 100 if total_days > 0 else 0
        on_track = goal.progress_percentage >= expected_progress

        return GoalProgressResponse(
            goal_id=goal.id,
            goal_name=goal.name,
            metric_type=goal.metric_type,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            progress_percentage=goal.progress_percentage,
            status=goal.status,
            days_remaining=max(0, days_remaining),
            daily_required_progress=daily_required if days_remaining > 0 else None,
            on_track=on_track,
            forecast_value=goal.forecast_value,
            forecast_updated_at=goal.forecast_updated_at,
        )

    async def get_forecasts(self, metric_type: Optional[GoalMetricType] = None) -> List[GoalForecastResponse]:
        """Get forecasts for all active goals."""
        query = select(Goal).where(Goal.status == GoalStatus.active)
        if metric_type:
            query = query.where(Goal.metric_type == metric_type)

        result = await self.db.execute(query)
        goals = result.scalars().all()

        forecasts = []
        for goal in goals:
            if goal.forecast_value is not None:
                will_achieve = goal.forecast_value >= goal.target_value
                confidence = min(0.95, goal.progress_percentage / 100)

                # Project completion date
                if goal.current_value > 0:
                    days_elapsed = (date.today() - goal.start_date).days
                    daily_rate = goal.current_value / days_elapsed if days_elapsed > 0 else 0
                    days_to_complete = (
                        (goal.target_value - goal.current_value) / daily_rate
                        if daily_rate > 0
                        else float('inf')
                    )
                    projected_date = (
                        date.today() + timedelta(days=int(days_to_complete))
                        if days_to_complete != float('inf')
                        else None
                    )
                else:
                    projected_date = None

                # Recommendation
                if will_achieve:
                    recommendation = "On track to achieve goal. Maintain current pace."
                elif goal.progress_percentage < 50:
                    recommendation = "Behind schedule. Consider increasing efforts or adjusting target."
                else:
                    recommendation = "Progress is moderate. Increase pace to ensure goal achievement."

                forecasts.append(
                    GoalForecastResponse(
                        goal_id=goal.id,
                        goal_name=goal.name,
                        current_value=goal.current_value,
                        target_value=goal.target_value,
                        forecast_value=goal.forecast_value,
                        forecast_confidence=confidence,
                        will_achieve=will_achieve,
                        projected_completion_date=projected_date,
                        recommended_action=recommendation,
                    )
                )

        return forecasts

    async def _calculate_forecast(self, goal: Goal) -> float:
        """Calculate forecasted final value based on current trend."""
        today = date.today()
        days_elapsed = (today - goal.start_date).days
        total_days = (goal.end_date - goal.start_date).days

        if days_elapsed <= 0 or goal.current_value == 0:
            return goal.current_value

        # Simple linear projection
        daily_rate = goal.current_value / days_elapsed
        forecast = daily_rate * total_days

        return round(forecast, 2)


# Import for projected date calculation
from datetime import timedelta
