"""merge migration heads

Revision ID: d68df1702da2
Revises: ced1280a683c, d0f4b41cee0c
Create Date: 2026-03-08 21:47:22.984885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd68df1702da2'
down_revision: Union[str, None] = ('ced1280a683c', 'd0f4b41cee0c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
