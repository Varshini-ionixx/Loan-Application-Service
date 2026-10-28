"""add customer eligibility fields

Revision ID: 4f1c2a9d7e83
Revises: 72517eeafe9e
Create Date: 2026-10-27 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f1c2a9d7e83"
down_revision: str | Sequence[str] | None = "72517eeafe9e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("customers", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("customers", sa.Column("monthly_income", sa.Float(), nullable=True))
    op.add_column("customers", sa.Column("existing_emi", sa.Float(), nullable=True))
    op.add_column("customers", sa.Column("credit_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("customers", "credit_score")
    op.drop_column("customers", "existing_emi")
    op.drop_column("customers", "monthly_income")
    op.drop_column("customers", "age")
