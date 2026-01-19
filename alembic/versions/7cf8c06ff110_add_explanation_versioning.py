"""add explanation versioning

Revision ID: 7cf8c06ff110
Revises: bb4932deabe1
Create Date: 2026-01-13 17:42:37.318157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cf8c06ff110'
down_revision: Union[str, Sequence[str], None] = 'bb4932deabe1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
