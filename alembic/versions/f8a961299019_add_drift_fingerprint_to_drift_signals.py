"""add drift_fingerprint to drift_signals

Revision ID: f8a961299019
Revises: 985ec6155758
Create Date: 2026-01-04 01:01:12.053694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a961299019'
down_revision: Union[str, Sequence[str], None] = '985ec6155758'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "drift_signals",
        sa.Column("drift_fingerprint", sa.String(), nullable=False),
    )

def downgrade():
    op.drop_column("drift_signals", "drift_fingerprint")
