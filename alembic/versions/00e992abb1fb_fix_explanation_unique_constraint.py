"""fix explanation unique constraint

Revision ID: 00e992abb1fb
Revises: 2141a264d77d
Create Date: 2026-01-14 22:31:22.265775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "00e992abb1fb"
down_revision = "2141a264d77d"
branch_labels = None
depends_on = None


def upgrade():
    # Create the correct unique constraint directly
    op.create_unique_constraint(
        "uq_explanations_key_version",
        "explanations",
        ["explanation_key", "version"],
    )


def downgrade():
    op.drop_constraint("uq_explanations_key_version", "explanations", type_="unique")


