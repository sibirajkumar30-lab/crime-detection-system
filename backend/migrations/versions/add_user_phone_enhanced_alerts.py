"""Add phone to users and enhanced alert fields.

Revision ID: add_user_phone_enhanced_alerts
Revises: 942effc5d261
Create Date: 2024-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_phone_enhanced_alerts'
down_revision = '08a7fdb06b59'
branch_labels = None
depends_on = None


def upgrade():
    # Add phone field to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
    
    # Add enhanced alert fields to alerts table
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('severity', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('alert_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recipient_phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('acknowledged', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('acknowledged_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('acknowledged_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('delivery_method', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('data', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
        
        # Create indexes for query performance
        batch_op.create_index('ix_alerts_severity', ['severity'], unique=False)
        batch_op.create_index('ix_alerts_category', ['category'], unique=False)
        batch_op.create_index('ix_alerts_acknowledged', ['acknowledged'], unique=False)
        batch_op.create_index('ix_alerts_expires_at', ['expires_at'], unique=False)
    
    # Set default values for existing records
    op.execute("UPDATE alerts SET severity = 'info' WHERE severity IS NULL")
    op.execute("UPDATE alerts SET category = 'operational' WHERE category IS NULL")
    op.execute("UPDATE alerts SET alert_type = 'general' WHERE alert_type IS NULL")
    op.execute("UPDATE alerts SET priority = 3 WHERE priority IS NULL")
    op.execute("UPDATE alerts SET acknowledged = 0 WHERE acknowledged IS NULL")
    op.execute("UPDATE alerts SET delivery_method = 'email' WHERE delivery_method IS NULL")


def downgrade():
    # Remove indexes
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.drop_index('ix_alerts_expires_at')
        batch_op.drop_index('ix_alerts_acknowledged')
        batch_op.drop_index('ix_alerts_category')
        batch_op.drop_index('ix_alerts_severity')
        
        # Remove columns
        batch_op.drop_column('expires_at')
        batch_op.drop_column('data')
        batch_op.drop_column('delivery_method')
        batch_op.drop_column('acknowledged_at')
        batch_op.drop_column('acknowledged_by')
        batch_op.drop_column('acknowledged')
        batch_op.drop_column('recipient_phone')
        batch_op.drop_column('priority')
        batch_op.drop_column('alert_type')
        batch_op.drop_column('category')
        batch_op.drop_column('severity')
    
    # Remove phone from users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('phone')
