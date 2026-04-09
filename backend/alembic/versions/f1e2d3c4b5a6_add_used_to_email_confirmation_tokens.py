"""add used to email_confirmation_tokens

Revision ID: f1e2d3c4b5a6
Revises: a13cb40eef8e
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, None] = 'a13cb40eef8e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'email_confirmation_tokens',
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('email_confirmation_tokens', 'used')
