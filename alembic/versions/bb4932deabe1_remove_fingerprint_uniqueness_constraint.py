"""remove fingerprint uniqueness constraint

Revision ID: bb4932deabe1
Revises: f55f12246dab
Create Date: 2026-01-13 16:17:00.375239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb4932deabe1'
down_revision: Union[str, Sequence[str], None] = 'f55f12246dab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("""
        DROP INDEX IF EXISTS ux_incident_active;
    """)

def downgrade():
    op.execute("""
        CREATE UNIQUE INDEX ux_incident_active
        ON incidents (source_id, drift_fingerprint)
        WHERE status <> 'RESOLVED';
    """)
