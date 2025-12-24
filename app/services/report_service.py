"""Service layer for report operations."""
import os
import json
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportType, ReportFormat, ReportStatus
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportScheduleCreate,
    ReportEmailRequest,
)


class ReportService:
    """Service for managing analytics reports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.reports_dir = "/home/ubuntu/analytics_service/reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    async def create_report(self, report_data: ReportCreate) -> Report:
        """Create a new report request."""
        report = Report(
            name=report_data.name,
            report_type=report_data.report_type,
            format=report_data.format,
            parameters=report_data.parameters,
            status=ReportStatus.pending,
            scheduled=report_data.scheduled or False,
            schedule_config=report_data.schedule_config,
            email_recipients=report_data.email_recipients,
            created_by=report_data.created_by,
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """Get a report by ID."""
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        scheduled: Optional[bool] = None,
        created_by: Optional[UUID] = None,
    ) -> List[Report]:
        """List reports with filters."""
        query = select(Report)
        filters = []

        if report_type:
            filters.append(Report.report_type == report_type)
        if status:
            filters.append(Report.status == status)
        if scheduled is not None:
            filters.append(Report.scheduled == scheduled)
        if created_by:
            filters.append(Report.created_by == created_by)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_report(self, report_id: UUID, report_data: ReportUpdate) -> Optional[Report]:
        """Update a report."""
        report = await self.get_report(report_id)
        if not report:
            return None

        update_data = report_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete a report and its file."""
        report = await self.get_report(report_id)
        if not report:
            return False

        # Delete file if exists
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)

        await self.db.delete(report)
        await self.db.commit()
        return True

    async def generate_report(self, report_id: UUID) -> Optional[Report]:
        """Generate a report (placeholder - actual generation would be more complex)."""
        report = await self.get_report(report_id)
        if not report:
            return None

        # Update status to generating
        report.status = ReportStatus.generating
        await self.db.commit()

        try:
            # Generate report file (simplified)
            file_name = f"{report.name.replace(' ', '_')}_{report.id}.{report.format.value}"
            file_path = os.path.join(self.reports_dir, file_name)

            # Simulated report generation based on format
            if report.format == ReportFormat.json:
                report_content = {
                    "report_name": report.name,
                    "report_type": report.report_type.value,
                    "generated_at": datetime.utcnow().isoformat(),
                    "parameters": report.parameters,
                    "data": {"placeholder": "Report data would be here"},
                }
                with open(file_path, 'w') as f:
                    json.dump(report_content, f, indent=2)
            elif report.format == ReportFormat.csv:
                with open(file_path, 'w') as f:
                    f.write("Date,Metric,Value\n")
                    f.write(f"{datetime.utcnow().date()},Sample Metric,100\n")
            else:
                # For PDF and Excel, just create placeholder files
                with open(file_path, 'w') as f:
                    f.write(f"Report: {report.name}\nGenerated: {datetime.utcnow()}\n")

            # Update report with file info
            report.file_path = file_path
            report.file_size = os.path.getsize(file_path)
            report.generated_at = datetime.utcnow()
            report.status = ReportStatus.completed

        except Exception as e:
            report.status = ReportStatus.failed
            # Log error (in production, use proper logging)
            print(f"Error generating report: {e}")

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def email_report(self, report_id: UUID, email_request: ReportEmailRequest) -> bool:
        """Send report via email (placeholder)."""
        report = await self.get_report(report_id)
        if not report or not report.file_path:
            return False

        # In production, integrate with email service
        # For now, just log the action
        print(f"Email sent: {report.name} to {email_request.recipients}")
        return True

    async def schedule_report(self, schedule_data: ReportScheduleCreate) -> Report:
        """Create a scheduled recurring report."""
        report_data = ReportCreate(
            name=schedule_data.name,
            report_type=schedule_data.report_type,
            format=schedule_data.format,
            parameters=schedule_data.parameters,
            scheduled=True,
            schedule_config=schedule_data.schedule_config,
            email_recipients=schedule_data.email_recipients,
            created_by=schedule_data.created_by,
        )
        return await self.create_report(report_data)
