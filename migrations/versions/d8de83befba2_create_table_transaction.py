"""create table transaction

Revision ID: d8de83befba2
Revises: f88dc6c095bb
Create Date: 2023-02-24 19:45:13.646731

"""
from __future__ import annotations

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8de83befba2"
down_revision = "f88dc6c095bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "transaction",
        sa.Column("quote_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("target_account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("complaint_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["complaint_id"],
            ["complaint.id"],
            name=op.f("fk_transaction_complaint_id_complaint"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_transaction")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transaction")
    # ### end Alembic commands ###
