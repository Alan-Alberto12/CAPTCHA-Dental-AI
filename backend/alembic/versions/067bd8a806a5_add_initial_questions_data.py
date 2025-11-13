"""add_initial_questions_data

Revision ID: 067bd8a806a5
Revises: 9209a434d045
Create Date: 2025-11-13 19:12:02.295967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '067bd8a806a5'
down_revision: Union[str, None] = '9209a434d045'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert initial questions - these will be added to EVERYONE's database
    # when they run migrations
    op.execute("""
        INSERT INTO questions (question_text, question_type, active, created_at)
        VALUES
            ('What tooth number is this?', 'tooth_number', true, NOW()),
            ('Is there a cavity present?', 'cavity_detection', true, NOW()),
            ('What is the condition of the gums?', 'gum_condition', true, NOW()),
            ('Is there any tooth decay?', 'decay_detection', true, NOW()),
            ('What is the overall dental health?', 'overall_health', true, NOW())
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    # Remove the questions if we need to rollback
    op.execute("""
        DELETE FROM questions
        WHERE question_text IN (
            'What tooth number is this?',
            'Is there a cavity present?',
            'What is the condition of the gums?',
            'Is there any tooth decay?',
            'What is the overall dental health?'
        );
    """)
