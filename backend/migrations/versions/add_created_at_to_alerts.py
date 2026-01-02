"""add missing columns to alerts

Revision ID: add_created_at_alerts
Revises: d1cf289aa2d9
Create Date: 2025-12-26 16:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_created_at_alerts'
down_revision = 'd1cf289aa2d9'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to alerts table
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        # Add created_at column
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        
        # Add reference columns
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('criminal_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('video_detection_id', sa.Integer(), nullable=True))
        
        # Add title column
        batch_op.add_column(sa.Column('title', sa.String(length=200), nullable=True))
        
        # Create foreign keys
        batch_op.create_foreign_key('fk_alerts_user_id', 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key('fk_alerts_criminal_id', 'criminals', ['criminal_id'], ['id'])
        batch_op.create_foreign_key('fk_alerts_video_detection_id', 'video_detections', ['video_detection_id'], ['id'])
        
        # Create indexes for performance
        batch_op.create_index('ix_alerts_created_at', ['created_at'], unique=False)
        batch_op.create_index('ix_alerts_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_alerts_criminal_id', ['criminal_id'], unique=False)
    
    # Update existing records: use sent_at as default value for created_at
    op.execute("UPDATE alerts SET created_at = sent_at WHERE created_at IS NULL")
    
    # Now make created_at non-nullable
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.alter_column('created_at', nullable=False)


def downgrade():
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        # Drop indexes
        batch_op.drop_index('ix_alerts_criminal_id')
        batch_op.drop_index('ix_alerts_user_id')
        batch_op.drop_index('ix_alerts_created_at')
        
        # Drop foreign keys
        batch_op.drop_constraint('fk_alerts_video_detection_id', type_='foreignkey')
        batch_op.drop_constraint('fk_alerts_criminal_id', type_='foreignkey')
        batch_op.drop_constraint('fk_alerts_user_id', type_='foreignkey')
        
        # Drop columns
        batch_op.drop_column('title')
        batch_op.drop_column('video_detection_id')
        batch_op.drop_column('criminal_id')
        batch_op.drop_column('user_id')
        batch_op.drop_column('created_at')
