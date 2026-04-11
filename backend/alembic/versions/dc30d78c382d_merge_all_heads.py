"""merge all heads

Revision ID: dc30d78c382d
Revises: 68b3fde92644, a13cb40eef8e
Create Date: 2026-04-11 13:33:03.092982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc30d78c382d'
down_revision: Union[str, None] = ('68b3fde92644', 'a13cb40eef8e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
