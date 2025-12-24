"""Add core analytics models: Metric, Dashboard, DataSync

Revision ID: c1fa66036222
Revises: 
Create Date: 2025-12-24 17:50:41.286402+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c1fa66036222'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    
    # Create Enums
    service_name_enum = postgresql.ENUM(
        'auth', 'content', 'partners_crm', 'projects', 'social_media', 'notification',
        name='service_name_enum'
    )
    service_name_enum.create(op.get_bind(), checkfirst=True)
    
    metric_type_enum = postgresql.ENUM(
        'donation', 'partner', 'project', 'beneficiary', 'social_post', 
        'notification', 'engagement', 'conversion', 'revenue',
        name='metric_type_enum'
    )
    metric_type_enum.create(op.get_bind(), checkfirst=True)
    
    dashboard_type_enum = postgresql.ENUM(
        'executive', 'partner', 'project', 'social_media', 'notification', 'custom',
        name='dashboard_type_enum'
    )
    dashboard_type_enum.create(op.get_bind(), checkfirst=True)
    
    data_sync_service_name_enum = postgresql.ENUM(
        'auth', 'content', 'partners_crm', 'projects', 'social_media', 'notification',
        name='data_sync_service_name_enum'
    )
    data_sync_service_name_enum.create(op.get_bind(), checkfirst=True)
    
    sync_type_enum = postgresql.ENUM(
        'full', 'incremental', 'manual',
        name='sync_type_enum'
    )
    sync_type_enum.create(op.get_bind(), checkfirst=True)
    
    sync_status_enum = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed',
        name='sync_status_enum'
    )
    sync_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_name', sa.Enum(
            'auth', 'content', 'partners_crm', 'projects', 'social_media', 'notification',
            name='service_name_enum'
        ), nullable=False, comment='Service that generated the metric'),
        sa.Column('metric_type', sa.Enum(
            'donation', 'partner', 'project', 'beneficiary', 'social_post', 
            'notification', 'engagement', 'conversion', 'revenue',
            name='metric_type_enum'
        ), nullable=False, comment='Type of metric'),
        sa.Column('metric_name', sa.String(length=255), nullable=False, comment='Name of the metric'),
        sa.Column('metric_value', sa.Float(), nullable=False, comment='Numeric value of the metric'),
        sa.Column('metric_unit', sa.String(length=50), nullable=True, 
                  comment='Unit of measurement (USD, count, percentage, etc.)'),
        sa.Column('dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Additional dimensions (partner_type, project_type, channel, etc.)'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, 
                  comment='Timestamp when metric was recorded'),
        sa.Column('date', sa.Date(), nullable=False, comment='Date for daily aggregations'),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Additional context'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for metrics table
    op.create_index('ix_metrics_id', 'metrics', ['id'])
    op.create_index('ix_metrics_service_name', 'metrics', ['service_name'])
    op.create_index('ix_metrics_metric_type', 'metrics', ['metric_type'])
    op.create_index('ix_metrics_metric_name', 'metrics', ['metric_name'])
    op.create_index('ix_metrics_timestamp', 'metrics', ['timestamp'])
    op.create_index('ix_metrics_date', 'metrics', ['date'])
    op.create_index('idx_metrics_service_type_date', 'metrics', ['service_name', 'metric_type', 'date'])
    op.create_index('idx_metrics_name_date', 'metrics', ['metric_name', 'date'])
    op.create_index('idx_metrics_timestamp', 'metrics', ['timestamp'])
    
    # Create dashboards table
    op.create_table(
        'dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Dashboard name'),
        sa.Column('dashboard_type', sa.Enum(
            'executive', 'partner', 'project', 'social_media', 'notification', 'custom',
            name='dashboard_type_enum'
        ), nullable=False, comment='Type of dashboard'),
        sa.Column('description', sa.Text(), nullable=True, comment='Dashboard description'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Dashboard configuration (widgets, layout, filters)'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false', 
                  comment='Whether this is the default dashboard for its type'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false', 
                  comment='Whether the dashboard is publicly accessible'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, 
                  comment='User ID who created the dashboard'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for dashboards table
    op.create_index('ix_dashboards_id', 'dashboards', ['id'])
    op.create_index('ix_dashboards_name', 'dashboards', ['name'])
    op.create_index('ix_dashboards_dashboard_type', 'dashboards', ['dashboard_type'])
    op.create_index('ix_dashboards_is_default', 'dashboards', ['is_default'])
    op.create_index('ix_dashboards_is_public', 'dashboards', ['is_public'])
    op.create_index('ix_dashboards_created_by', 'dashboards', ['created_by'])
    
    # Create data_syncs table
    op.create_table(
        'data_syncs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_name', sa.Enum(
            'auth', 'content', 'partners_crm', 'projects', 'social_media', 'notification',
            name='data_sync_service_name_enum'
        ), nullable=False, comment='Service being synchronized'),
        sa.Column('sync_type', sa.Enum(
            'full', 'incremental', 'manual',
            name='sync_type_enum'
        ), nullable=False, comment='Type of synchronization'),
        sa.Column('status', sa.Enum(
            'pending', 'running', 'completed', 'failed',
            name='sync_status_enum'
        ), nullable=False, server_default='pending', comment='Current status of synchronization'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, 
                  comment='When synchronization started'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, 
                  comment='When synchronization completed'),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0', 
                  comment='Number of records processed'),
        sa.Column('records_failed', sa.Integer(), nullable=False, server_default='0', 
                  comment='Number of records that failed'),
        sa.Column('last_sync_timestamp', sa.DateTime(timezone=True), nullable=True, 
                  comment='Timestamp of last successful sync'),
        sa.Column('error_message', sa.Text(), nullable=True, 
                  comment='Error message if synchronization failed'),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Additional metadata'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for data_syncs table
    op.create_index('ix_data_syncs_id', 'data_syncs', ['id'])
    op.create_index('ix_data_syncs_service_name', 'data_syncs', ['service_name'])
    op.create_index('ix_data_syncs_sync_type', 'data_syncs', ['sync_type'])
    op.create_index('ix_data_syncs_status', 'data_syncs', ['status'])
    op.create_index('ix_data_syncs_last_sync_timestamp', 'data_syncs', ['last_sync_timestamp'])


def downgrade() -> None:
    """Downgrade database schema."""
    
    # Drop tables
    op.drop_table('data_syncs')
    op.drop_table('dashboards')
    op.drop_table('metrics')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS sync_status_enum')
    op.execute('DROP TYPE IF EXISTS sync_type_enum')
    op.execute('DROP TYPE IF EXISTS data_sync_service_name_enum')
    op.execute('DROP TYPE IF EXISTS dashboard_type_enum')
    op.execute('DROP TYPE IF EXISTS metric_type_enum')
    op.execute('DROP TYPE IF EXISTS service_name_enum')
