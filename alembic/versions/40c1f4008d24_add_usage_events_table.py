"""add usage_events table

Revision ID: 40c1f4008d24
Revises: 8864e6262fbc
Create Date: 2026-01-15 23:10:22.095891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40c1f4008d24'
down_revision: Union[str, Sequence[str], None] = '8864e6262fbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "usage_events",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_foreign_key(
        "fk_usage_events_org",
        "usage_events",
        "orgs",
        ["org_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_usage_events_org_id",
        "usage_events",
        ["org_id"],
    )


def downgrade():
    op.drop_index("ix_usage_events_org_id", table_name="usage_events")
    op.drop_constraint("fk_usage_events_org", "usage_events", type_="foreignkey")
    op.drop_table("usage_events")

