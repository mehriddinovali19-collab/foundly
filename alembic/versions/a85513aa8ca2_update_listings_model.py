"""update listings model

Revision ID: a85513aa8ca2

Revises: d6ff1d1a8898

Create Date: 2026-08-24 23:53:51.289833

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.

revision: str = "a85513aa8ca2"
down_revision: Union[str, Sequence[str], None] = "d6ff1d1a8898"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "listings",
        "dates",
        new_column_name="date",
    )

    op.create_index(
        op.f("ix_listings_id"),
        "listings",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_listings_user_id"),
        "listings",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "listings",
        "date",
        new_column_name="dates",
    )

    op.drop_index(
        op.f("ix_listings_user_id"),
        table_name="listings",
    )

    op.drop_index(
        op.f("ix_listings_id"),
        table_name="listings",
    )