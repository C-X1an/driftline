from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "985ec6155758"
down_revision = "d1acb77a7dec"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "explanations",
        sa.Column("explanation_key", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_column("explanations", "explanation_key")
