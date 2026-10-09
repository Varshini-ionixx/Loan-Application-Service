"""Align customer schema and create loans table."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ac6ba97e0258"
down_revision: str | Sequence[str] | None = "cbb63ae3881a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Preserve existing phone values while renaming the column.
    op.drop_constraint("customers_phone_number_key", "customers", type_="unique")
    op.alter_column(
        "customers",
        "phone_number",
        new_column_name="phone",
        existing_type=sa.String(length=10),
        existing_nullable=False,
    )
    op.create_unique_constraint("customers_phone_key", "customers", ["phone"])

    # CURRENT_TIMESTAMP fills existing rows and provides a value
    # while this non-null column is added.
    op.add_column(
        "customers",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.alter_column(
        "customers",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=False,
    )

    # Match the model's indexed email and ID fields.
    op.drop_constraint("customers_email_key", "customers", type_="unique")
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)
    op.create_index("ix_customers_id", "customers", ["id"], unique=False)

    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("tenure_months", sa.Integer(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=False),
        sa.Column("monthly_emi", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("rejection_reason", sa.String(length=255), nullable=True),
        sa.Column(
            "applied_on",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column("loans", "status", server_default=None)
    op.alter_column("loans", "applied_on", server_default=None)
    op.create_index("ix_loans_id", "loans", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_loans_id", table_name="loans")
    op.drop_table("loans")

    op.drop_index("ix_customers_id", table_name="customers")
    op.drop_index("ix_customers_email", table_name="customers")
    op.create_unique_constraint("customers_email_key", "customers", ["email"])

    op.drop_constraint("customers_phone_key", "customers", type_="unique")
    op.alter_column(
        "customers",
        "phone",
        new_column_name="phone_number",
        existing_type=sa.String(length=10),
        existing_nullable=False,
    )
    op.create_unique_constraint(
        "customers_phone_number_key", "customers", ["phone_number"]
    )
    op.drop_column("customers", "created_at")
