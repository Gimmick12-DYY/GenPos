"""Add metadata_json to asset_packs for activation audit trail

Revision ID: 004
Revises: 003
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "asset_packs",
        sa.Column("metadata_json", JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("asset_packs", "metadata_json")
