"""make detection_log_id nullable in alerts

Revision ID: fix_detection_log_nullable
Revises: add_created_at_alerts
Create Date: 2025-12-26 17:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_detection_log_nullable'
down_revision = 'add_created_at_alerts'
branch_labels = None
depends_on = None


def upgrade():
    # Make detection_log_id nullable since not all alerts are related to detections
    # (e.g., criminal add/update/delete alerts)
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.alter_column('detection_log_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)


def downgrade():
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.alter_column('detection_log_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)
