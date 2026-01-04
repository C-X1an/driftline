"""make risk_assessment_id nullable on explanations

Revision ID: d7c10f66fbcf
Revises: 94419ed33487
Create Date: 2026-01-04 18:50:16.977576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7c10f66fbcf'
down_revision: Union[str, Sequence[str], None] = '94419ed33487'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "explanations",
        "risk_assessment_id",
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "explanations",
        "risk_assessment_id",
        nullable=False,
    )
