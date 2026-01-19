"""add version column to explanations

Revision ID: 2141a264d77d
Revises: 47adeecb18bc
Create Date: 2026-01-14 22:27:13.892236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2141a264d77d'
down_revision: Union[str, Sequence[str], None] = '47adeecb18bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "explanations",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.alter_column("explanations", "version", server_default=None)


def downgrade():
    op.drop_column("explanations", "version")

