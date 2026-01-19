"""add orgs table and org_id to incidents

Revision ID: 8864e6262fbc
Revises: d9fccea4c7fa
Create Date: 2026-01-15 22:59:59.616511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8864e6262fbc'
down_revision: Union[str, Sequence[str], None] = 'd9fccea4c7fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Create orgs table
    op.create_table(
        "orgs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False, server_default="FREE"),
    )

    # 2. Add org_id as nullable FIRST
    op.add_column(
        "incidents",
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 3. Create a default org
    connection = op.get_bind()
    result = connection.execute(
        sa.text(
            """
            INSERT INTO orgs (id, name, plan)
            VALUES (gen_random_uuid(), 'Default Org', 'FREE')
            RETURNING id
            """
        )
    )
    default_org_id = result.scalar()

    # 4. Backfill existing incidents
    connection.execute(
        sa.text(
            """
            UPDATE incidents
            SET org_id = :org_id
            WHERE org_id IS NULL
            """
        ),
        {"org_id": default_org_id},
    )

    # 5. Set org_id to NOT NULL
    op.alter_column("incidents", "org_id", nullable=False)

    # 6. Add FK constraint
    op.create_foreign_key(
        "fk_incidents_org",
        "incidents",
        "orgs",
        ["org_id"],
        ["id"],
        ondelete="CASCADE",
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
