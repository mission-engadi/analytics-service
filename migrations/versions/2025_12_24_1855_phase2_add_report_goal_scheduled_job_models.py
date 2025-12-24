"""Add Phase 2 models: Report, Goal, ScheduledJob

Revision ID: phase2_models_20251224
Revises: c1fa66036222
Create Date: 2025-12-24 18:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase2_models_20251224'
down_revision = 'c1fa66036222'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums for Report model
    report_type_enum = postgresql.ENUM(
        'daily', 'weekly', 'monthly', 'annual', 'custom',
        name='report_type_enum',
        create_type=False
    )
    report_type_enum.create(op.get_bind(), checkfirst=True)

    report_format_enum = postgresql.ENUM(
        'pdf', 'excel', 'csv', 'json',
        name='report_format_enum',
        create_type=False
    )
    report_format_enum.create(op.get_bind(), checkfirst=True)

    report_status_enum = postgresql.ENUM(
        'pending', 'generating', 'completed', 'failed',
        name='report_status_enum',
        create_type=False
    )
    report_status_enum.create(op.get_bind(), checkfirst=True)

    # Create enums for Goal model
    goal_metric_type_enum = postgresql.ENUM(
        'donation', 'partner', 'project', 'beneficiary', 'social_post',
        'notification', 'engagement', 'conversion', 'revenue',
        name='goal_metric_type_enum',
        create_type=False
    )
    goal_metric_type_enum.create(op.get_bind(), checkfirst=True)

    goal_status_enum = postgresql.ENUM(
        'active', 'achieved', 'failed', 'cancelled',
        name='goal_status_enum',
        create_type=False
    )
    goal_status_enum.create(op.get_bind(), checkfirst=True)

    # Create enums for ScheduledJob model
    job_type_enum = postgresql.ENUM(
        'data_sync', 'report_generation', 'goal_update', 'custom',
        name='job_type_enum',
        create_type=False
    )
    job_type_enum.create(op.get_bind(), checkfirst=True)

    job_status_enum = postgresql.ENUM(
        'success', 'failed', 'running', 'pending',
        name='job_status_enum',
        create_type=False
    )
    job_status_enum.create(op.get_bind(), checkfirst=True)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Report name'),
        sa.Column('report_type', report_type_enum, nullable=False, comment='Type of report'),
        sa.Column('format', report_format_enum, nullable=False, comment='Report file format'),
        sa.Column('status', report_status_enum, nullable=False, comment='Report generation status'),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Report parameters (date range, filters, etc.)'),
        sa.Column('file_path', sa.String(length=500), nullable=True, comment='Path to generated report file'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='File size in bytes'),
        sa.Column('generated_at', sa.DateTime(), nullable=True, comment='When the report was generated'),
        sa.Column('scheduled', sa.Boolean(), nullable=True, comment='Is this a scheduled report'),
        sa.Column('schedule_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Cron schedule configuration if scheduled'),
        sa.Column('email_recipients', postgresql.ARRAY(sa.String()), nullable=True, comment='Email addresses to send report to'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='User who created the report'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the report was created'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the report was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for reports table
    op.create_index('ix_reports_id', 'reports', ['id'])
    op.create_index('ix_reports_name', 'reports', ['name'])
    op.create_index('ix_reports_report_type', 'reports', ['report_type'])
    op.create_index('ix_reports_format', 'reports', ['format'])
    op.create_index('ix_reports_status', 'reports', ['status'])
    op.create_index('ix_reports_generated_at', 'reports', ['generated_at'])
    op.create_index('ix_reports_scheduled', 'reports', ['scheduled'])
    op.create_index('ix_reports_created_by', 'reports', ['created_by'])
    op.create_index('ix_reports_created_at', 'reports', ['created_at'])
    op.create_index('ix_reports_type_status', 'reports', ['report_type', 'status'])

    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Goal name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Goal description'),
        sa.Column('metric_type', goal_metric_type_enum, nullable=False, comment='Type of metric being tracked'),
        sa.Column('target_value', sa.Float(), nullable=False, comment='Target value to achieve'),
        sa.Column('current_value', sa.Float(), nullable=False, comment='Current progress value'),
        sa.Column('unit', sa.String(length=50), nullable=True, comment='Unit of measurement (USD, count, percentage, etc.)'),
        sa.Column('start_date', sa.Date(), nullable=False, comment='Goal start date'),
        sa.Column('end_date', sa.Date(), nullable=False, comment='Goal end date'),
        sa.Column('status', goal_status_enum, nullable=False, comment='Goal achievement status'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, comment='Progress as percentage'),
        sa.Column('alert_threshold', sa.Float(), nullable=True, comment='Alert when progress reaches this percentage'),
        sa.Column('alert_sent', sa.Boolean(), nullable=True, comment='Has alert been sent'),
        sa.Column('forecast_value', sa.Float(), nullable=True, comment='Predicted final value based on current trend'),
        sa.Column('forecast_updated_at', sa.DateTime(), nullable=True, comment='When the forecast was last updated'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='User who created the goal'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the goal was created'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the goal was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for goals table
    op.create_index('ix_goals_id', 'goals', ['id'])
    op.create_index('ix_goals_name', 'goals', ['name'])
    op.create_index('ix_goals_metric_type', 'goals', ['metric_type'])
    op.create_index('ix_goals_start_date', 'goals', ['start_date'])
    op.create_index('ix_goals_end_date', 'goals', ['end_date'])
    op.create_index('ix_goals_status', 'goals', ['status'])
    op.create_index('ix_goals_created_by', 'goals', ['created_by'])
    op.create_index('ix_goals_created_at', 'goals', ['created_at'])
    op.create_index('ix_goals_metric_status', 'goals', ['metric_type', 'status'])

    # Create scheduled_jobs table
    op.create_table(
        'scheduled_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Job name'),
        sa.Column('job_type', job_type_enum, nullable=False, comment='Type of job'),
        sa.Column('schedule', sa.String(length=100), nullable=False, comment='Cron expression for job schedule'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='Is the job active'),
        sa.Column('last_run_at', sa.DateTime(), nullable=True, comment='When the job last ran'),
        sa.Column('next_run_at', sa.DateTime(), nullable=True, comment='When the job will run next'),
        sa.Column('last_status', job_status_enum, nullable=True, comment='Status of last execution'),
        sa.Column('run_count', sa.Integer(), nullable=True, comment='Total number of executions'),
        sa.Column('success_count', sa.Integer(), nullable=True, comment='Number of successful executions'),
        sa.Column('failure_count', sa.Integer(), nullable=True, comment='Number of failed executions'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Job configuration and parameters'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='When the job was created'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='When the job was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for scheduled_jobs table
    op.create_index('ix_scheduled_jobs_id', 'scheduled_jobs', ['id'])
    op.create_index('ix_scheduled_jobs_name', 'scheduled_jobs', ['name'])
    op.create_index('ix_scheduled_jobs_job_type', 'scheduled_jobs', ['job_type'])
    op.create_index('ix_scheduled_jobs_is_active', 'scheduled_jobs', ['is_active'])
    op.create_index('ix_scheduled_jobs_last_run_at', 'scheduled_jobs', ['last_run_at'])
    op.create_index('ix_scheduled_jobs_next_run_at', 'scheduled_jobs', ['next_run_at'])
    op.create_index('ix_scheduled_jobs_last_status', 'scheduled_jobs', ['last_status'])
    op.create_index('ix_scheduled_jobs_created_at', 'scheduled_jobs', ['created_at'])
    op.create_index('ix_scheduled_jobs_type_active', 'scheduled_jobs', ['job_type', 'is_active'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_scheduled_jobs_type_active', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_created_at', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_last_status', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_next_run_at', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_last_run_at', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_is_active', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_job_type', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_name', table_name='scheduled_jobs')
    op.drop_index('ix_scheduled_jobs_id', table_name='scheduled_jobs')
    op.drop_table('scheduled_jobs')

    op.drop_index('ix_goals_metric_status', table_name='goals')
    op.drop_index('ix_goals_created_at', table_name='goals')
    op.drop_index('ix_goals_created_by', table_name='goals')
    op.drop_index('ix_goals_status', table_name='goals')
    op.drop_index('ix_goals_end_date', table_name='goals')
    op.drop_index('ix_goals_start_date', table_name='goals')
    op.drop_index('ix_goals_metric_type', table_name='goals')
    op.drop_index('ix_goals_name', table_name='goals')
    op.drop_index('ix_goals_id', table_name='goals')
    op.drop_table('goals')

    op.drop_index('ix_reports_type_status', table_name='reports')
    op.drop_index('ix_reports_created_at', table_name='reports')
    op.drop_index('ix_reports_created_by', table_name='reports')
    op.drop_index('ix_reports_scheduled', table_name='reports')
    op.drop_index('ix_reports_generated_at', table_name='reports')
    op.drop_index('ix_reports_status', table_name='reports')
    op.drop_index('ix_reports_format', table_name='reports')
    op.drop_index('ix_reports_report_type', table_name='reports')
    op.drop_index('ix_reports_name', table_name='reports')
    op.drop_index('ix_reports_id', table_name='reports')
    op.drop_table('reports')

    # Drop enums
    sa.Enum(name='job_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='job_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='goal_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='goal_metric_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='report_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='report_format_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='report_type_enum').drop(op.get_bind(), checkfirst=True)
