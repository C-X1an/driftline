"""add diff column to snapshots

Revision ID: dedb0d424016
Revises: d7c10f66fbcf
Create Date: 2026-01-11 22:46:20.351524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'dedb0d424016'
down_revision: Union[str, Sequence[str], None] = 'd7c10f66fbcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "snapshots",
        sa.Column("diff", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade():
    op.drop_column("snapshots", "diff")