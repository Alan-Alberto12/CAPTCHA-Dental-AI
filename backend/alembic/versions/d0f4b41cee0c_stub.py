"""stub for missing migration

Revision ID: d0f4b41cee0c
Revises: ced1280a683c
Create Date: 2026-01-01

"""
from typing import Sequence, Union

revision: str = 'd0f4b41cee0c'
down_revision: Union[str, None] = 'ced1280a683c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
