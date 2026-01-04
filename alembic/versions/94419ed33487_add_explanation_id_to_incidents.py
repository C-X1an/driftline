"""add explanation_id to incidents

Revision ID: 94419ed33487
Revises: f8a961299019
Create Date: 2026-01-04 17:39:35.570705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94419ed33487'
down_revision: Union[str, Sequence[str], None] = 'f8a961299019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Column already exists; migration kept for history alignment
    pass


def downgrade():
    pass

