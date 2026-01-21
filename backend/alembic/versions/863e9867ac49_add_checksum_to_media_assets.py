"""add checksum to media_assets

Revision ID: 863e9867ac49
Revises: 01eefdf82888
Create Date: 2026-01-08 23:04:16.062082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '863e9867ac49'
down_revision: Union[str, Sequence[str], None] = '01eefdf82888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add checksum column with temporary default
    op.add_column(
        'media_assets',
        sa.Column('checksum', sa.Text(), nullable=False, server_default="")
    )

    # Remove the default (important!)
    op.alter_column(
        'media_assets',
        'checksum',
        server_default=None
    )


def downgrade() -> None:
    op.drop_column('media_assets', 'checksum')