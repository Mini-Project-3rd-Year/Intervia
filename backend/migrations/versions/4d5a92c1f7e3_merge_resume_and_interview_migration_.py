"""merge resume and interview migration heads

Revision ID: 4d5a92c1f7e3
Revises: 2a12c11e4f6a, a0fdd6388fe1
Create Date: 2026-10-28 16:34:50.807436
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '4d5a92c1f7e3'
down_revision: Union[str, None] = ('2a12c11e4f6a', 'a0fdd6388fe1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
