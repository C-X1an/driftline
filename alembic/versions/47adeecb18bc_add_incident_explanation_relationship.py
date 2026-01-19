"""add incident explanation relationship

Revision ID: 47adeecb18bc
Revises: 7cf8c06ff110
Create Date: 2026-01-14 22:21:40.263328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47adeecb18bc'
down_revision: Union[str, Sequence[str], None] = '7cf8c06ff110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "explanations",
        sa.Column("incident_id", sa.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_explanations_incident",
        "explanations",
        "incidents",
        ["incident_id"],
        ["id"],
    )

def downgrade():
    op.drop_constraint("fk_explanations_incident", "explanations", type_="foreignkey")
    op.drop_column("explanations", "incident_id")

