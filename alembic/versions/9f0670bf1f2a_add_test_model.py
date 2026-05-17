"""add test_model

Revision ID: 9f0670bf1f2a
Revises: c202cdd93949
Create Date: 2026-05-17 01:11:33.074348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f0670bf1f2a'
down_revision: Union[str, Sequence[str], None] = 'c202cdd93949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'test_model',

        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=True)

    )
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('test_model')
    
