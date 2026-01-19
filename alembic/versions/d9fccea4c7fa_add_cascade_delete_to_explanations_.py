"""add cascade delete to explanations.incident_id

Revision ID: d9fccea4c7fa
Revises: 76a8fcc65b7d
Create Date: 2026-01-15 22:47:15.762773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9fccea4c7fa'
down_revision: Union[str, Sequence[str], None] = '76a8fcc65b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint("fk_explanations_incident", "explanations", type_="foreignkey")
    op.create_foreign_key(
        "fk_explanations_incident",
        "explanations",
        "incidents",
        ["incident_id"],
        ["id"],
        ondelete="CASCADE",
    )



def downgrade():
    op.drop_constraint("fk_explanations_incident", "explanations", type_="foreignkey")
    op.create_foreign_key(
        "fk_explanations_incident",
        "explanations",
        "incidents",
        ["incident_id"],
        ["id"],
    )
