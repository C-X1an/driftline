"""remove explanation_id from incidents

Revision ID: 76a8fcc65b7d
Revises: 00e992abb1fb
Create Date: 2026-01-14 22:33:22.013879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76a8fcc65b7d"
down_revision = "00e992abb1fb"
branch_labels = None
depends_on = None


def upgrade():
    # Drop FK first
    op.drop_constraint("incidents_explanation_id_fkey", "incidents", type_="foreignkey")

    # Then drop column
    op.drop_column("incidents", "explanation_id")


def downgrade():
    op.add_column(
        "incidents",
        op.sa.Column("explanation_id", op.sa.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "incidents_explanation_id_fkey",
        "incidents",
        "explanations",
        ["explanation_id"],
        ["id"],
    )
