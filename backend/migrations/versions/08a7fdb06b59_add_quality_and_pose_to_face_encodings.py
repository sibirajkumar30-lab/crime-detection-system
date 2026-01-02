"""add_quality_and_pose_to_face_encodings

Revision ID: 08a7fdb06b59
Revises: 9ab7d80431e0
Create Date: 2025-12-23 17:54:10.803025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08a7fdb06b59'
down_revision = '9ab7d80431e0'
branch_labels = None
depends_on = None


def upgrade():
    # Check and add columns only if they don't exist
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('face_encodings')]
    
    if 'quality_score' not in columns:
        op.add_column('face_encodings', sa.Column('quality_score', sa.Float(), nullable=True))
    
    if 'pose_type' not in columns:
        op.add_column('face_encodings', sa.Column('pose_type', sa.String(50), nullable=True))
    
    if 'is_primary' not in columns:
        # Add as nullable first
        op.add_column('face_encodings', sa.Column('is_primary', sa.Boolean(), nullable=True))
        # Set default for existing rows
        op.execute("UPDATE face_encodings SET is_primary = 0 WHERE is_primary IS NULL")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('face_encodings')]
    
    if 'is_primary' in columns:
        op.drop_column('face_encodings', 'is_primary')
    if 'pose_type' in columns:
        op.drop_column('face_encodings', 'pose_type')
    if 'quality_score' in columns:
        op.drop_column('face_encodings', 'quality_score')
