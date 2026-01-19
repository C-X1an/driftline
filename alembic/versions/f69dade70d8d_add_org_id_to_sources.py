"""add org_id to sources

Revision ID: f69dade70d8d
Revises: 40c1f4008d24
Create Date: 2026-01-15 23:39:04.736676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f69dade70d8d'
down_revision: Union[str, Sequence[str], None] = '40c1f4008d24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Add org_id as nullable first
    op.add_column(
        "sources",
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Fetch default org id
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id FROM orgs ORDER BY name ASC LIMIT 1")
    )
    default_org_id = result.scalar()

    if not default_org_id:
        raise RuntimeError("No org found to backfill sources.org_id")

    # 3. Backfill existing sources
    connection.execute(
        sa.text(
            """
            UPDATE sources
            SET org_id = :org_id
            WHERE org_id IS NULL
            """
        ),
        {"org_id": default_org_id},
    )

    # 4. Set NOT NULL
    op.alter_column("sources", "org_id", nullable=False)

    # 5. Add FK
    op.create_foreign_key(
        "fk_sources_org",
        "sources",
        "orgs",
        ["org_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("fk_sources_org", "sources", type_="foreignkey")
    op.drop_column("sources", "org_id")
