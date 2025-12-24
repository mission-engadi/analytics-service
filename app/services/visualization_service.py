"""Service layer for data visualization operations."""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.metric import Metric, ServiceName, MetricType


class VisualizationService:
    """Service for generating visualization data configurations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_line_chart_data(
        self,
        metric_type: MetricType,
        service_name: Optional[ServiceName] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "day",
    ) -> Dict[str, Any]:
        """Generate line chart data configuration."""
        query = select(Metric).where(Metric.metric_type == metric_type)

        if service_name:
            query = query.where(Metric.service_name == service_name)
        if metric_name:
            query = query.where(Metric.metric_name == metric_name)
        if start_date:
            query = query.where(Metric.date >= start_date)
        if end_date:
            query = query.where(Metric.date <= end_date)

        query = query.order_by(Metric.timestamp)
        result = await self.db.execute(query)
        metrics = result.scalars().all()

        # Group by interval
        data_points = []
        if interval == "day":
            grouped = {}
            for m in metrics:
                key = m.date.isoformat()
                if key not in grouped:
                    grouped[key] = []
                grouped[key].append(m.value)
            
            data_points = [
                {"date": key, "value": sum(values) / len(values)}
                for key, values in sorted(grouped.items())
            ]
        else:
            # For other intervals, return raw data
            data_points = [
                {"date": m.date.isoformat(), "value": m.value}
                for m in metrics
            ]

        return {
            "chart_type": "line",
            "title": f"{metric_type.value.title()} Over Time",
            "x_axis": {"label": "Date", "type": "datetime"},
            "y_axis": {"label": "Value", "type": "linear"},
            "data": data_points,
            "config": {
                "responsive": True,
                "show_legend": True,
                "show_grid": True,
            },
        }

    async def get_bar_chart_data(
        self,
        metric_type: MetricType,
        group_by: str = "service",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate bar chart data configuration."""
        if group_by == "service":
            # Group by service
            data_points = []
            for service in ServiceName:
                query = select(func.sum(Metric.value)).where(
                    and_(
                        Metric.metric_type == metric_type,
                        Metric.service_name == service,
                    )
                )
                if start_date:
                    query = query.where(Metric.date >= start_date)
                if end_date:
                    query = query.where(Metric.date <= end_date)

                result = await self.db.execute(query)
                total = result.scalar() or 0

                data_points.append({
                    "category": service.value,
                    "value": float(total),
                })
        else:
            # Default grouping
            data_points = []

        return {
            "chart_type": "bar",
            "title": f"{metric_type.value.title()} by {group_by.title()}",
            "x_axis": {"label": group_by.title(), "type": "category"},
            "y_axis": {"label": "Total Value", "type": "linear"},
            "data": data_points,
            "config": {
                "responsive": True,
                "show_legend": False,
                "show_grid": True,
                "orientation": "vertical",
            },
        }

    async def get_pie_chart_data(
        self,
        metric_type: MetricType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate pie chart data configuration."""
        data_points = []
        total_sum = 0

        for service in ServiceName:
            query = select(func.sum(Metric.value)).where(
                and_(
                    Metric.metric_type == metric_type,
                    Metric.service_name == service,
                )
            )
            if start_date:
                query = query.where(Metric.date >= start_date)
            if end_date:
                query = query.where(Metric.date <= end_date)

            result = await self.db.execute(query)
            total = result.scalar() or 0
            total_sum += total

            data_points.append({
                "label": service.value,
                "value": float(total),
            })

        # Calculate percentages
        for point in data_points:
            point["percentage"] = round(
                (point["value"] / total_sum * 100) if total_sum > 0 else 0,
                2
            )

        return {
            "chart_type": "pie",
            "title": f"{metric_type.value.title()} Distribution",
            "data": data_points,
            "config": {
                "responsive": True,
                "show_legend": True,
                "show_labels": True,
                "show_percentages": True,
            },
        }

    async def get_area_chart_data(
        self,
        metric_type: MetricType,
        services: Optional[List[ServiceName]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate area chart data configuration."""
        if not services:
            services = list(ServiceName)

        series_data = []
        for service in services:
            query = select(Metric).where(
                and_(
                    Metric.metric_type == metric_type,
                    Metric.service_name == service,
                )
            )
            if start_date:
                query = query.where(Metric.date >= start_date)
            if end_date:
                query = query.where(Metric.date <= end_date)

            query = query.order_by(Metric.timestamp)
            result = await self.db.execute(query)
            metrics = result.scalars().all()

            data_points = [
                {"date": m.date.isoformat(), "value": m.value}
                for m in metrics
            ]

            series_data.append({
                "name": service.value,
                "data": data_points,
            })

        return {
            "chart_type": "area",
            "title": f"{metric_type.value.title()} Trends",
            "x_axis": {"label": "Date", "type": "datetime"},
            "y_axis": {"label": "Value", "type": "linear"},
            "series": series_data,
            "config": {
                "responsive": True,
                "show_legend": True,
                "show_grid": True,
                "stacked": False,
            },
        }

    async def get_heatmap_data(
        self,
        metric_type: MetricType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate heatmap data configuration."""
        query = select(Metric).where(Metric.metric_type == metric_type)
        
        if start_date:
            query = query.where(Metric.date >= start_date)
        if end_date:
            query = query.where(Metric.date <= end_date)

        result = await self.db.execute(query)
        metrics = result.scalars().all()

        # Create matrix data (service x day of week)
        heatmap_data = {}
        for m in metrics:
            service = m.service_name.value
            day = m.timestamp.strftime("%A")
            
            key = f"{service}_{day}"
            if key not in heatmap_data:
                heatmap_data[key] = []
            heatmap_data[key].append(m.value)

        # Calculate averages
        data_points = []
        for key, values in heatmap_data.items():
            service, day = key.split("_")
            data_points.append({
                "x": day,
                "y": service,
                "value": sum(values) / len(values),
            })

        return {
            "chart_type": "heatmap",
            "title": f"{metric_type.value.title()} Heatmap",
            "x_axis": {"label": "Day of Week", "type": "category"},
            "y_axis": {"label": "Service", "type": "category"},
            "data": data_points,
            "config": {
                "responsive": True,
                "show_legend": True,
                "color_scale": "viridis",
            },
        }
