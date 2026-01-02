"""merge_migrations

Revision ID: d1cf289aa2d9
Revises: 942effc5d261, add_user_phone_enhanced_alerts
Create Date: 2025-12-26 16:16:57.029496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1cf289aa2d9'
down_revision = ('942effc5d261', 'add_user_phone_enhanced_alerts')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
