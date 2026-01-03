"""add unique constraint to explanation_key

Revision ID: d1acb77a7dec
Revises: e1b814576245
Create Date: 2026-01-04 00:44:57.084874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1acb77a7dec'
down_revision: Union[str, Sequence[str], None] = 'e1b814576245'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
