"""add last_explained_tier to incidents

Revision ID: de261962b87e
Revises: f69dade70d8d
Create Date: 2026-01-19 22:19:19.180970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de261962b87e'
down_revision: Union[str, Sequence[str], None] = 'f69dade70d8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "incidents",
        sa.Column("last_explained_tier", sa.String(), nullable=True),
    )

def downgrade():
    op.drop_column("incidents", "last_explained_tier")

