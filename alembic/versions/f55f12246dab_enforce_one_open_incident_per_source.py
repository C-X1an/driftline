"""enforce one open incident per source

Revision ID: f55f12246dab
Revises: dedb0d424016
Create Date: 2026-01-13 16:07:29.975740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f55f12246dab'
down_revision: Union[str, Sequence[str], None] = 'dedb0d424016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Enforce only one OPEN/ACKED incident per source
    op.execute("""
        CREATE UNIQUE INDEX one_open_incident_per_source
        ON incidents (source_id)
        WHERE status IN ('OPEN', 'ACKED');
    """)

    # 2. Support fast lifecycle queries
    op.create_index(
        "ix_incidents_source_status_last_seen",
        "incidents",
        ["source_id", "status", "last_seen_at"],
    )


def downgrade():
    op.drop_index("ix_incidents_source_status_last_seen", table_name="incidents")

    op.execute("""
        DROP INDEX IF EXISTS one_open_incident_per_source;
    """)
