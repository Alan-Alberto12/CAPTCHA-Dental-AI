"""merge migration heads

Revision ID: c00bac95c7b8
Revises: d68df1702da2
Create Date: 2026-03-08 21:49:07.569430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c00bac95c7b8'
down_revision: Union[str, None] = 'd68df1702da2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
