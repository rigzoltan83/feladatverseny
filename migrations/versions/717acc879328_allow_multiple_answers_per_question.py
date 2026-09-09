"""allow multiple answers per question

Revision ID: 717acc879328
Revises: 7c9f4a1d2e6b
Create Date: 2026-09-09 06:02:43.658118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '717acc879328'
down_revision = '7c9f4a1d2e6b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "uq_competitor_answer_question",
        "competitor_answer",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_competitor_answer_selection",
        "competitor_answer",
        [
            "attempt_id",
            "generated_test_question_id",
            "generated_test_answer_id",
        ],
    )


def downgrade():
    op.drop_constraint(
        "uq_competitor_answer_selection",
        "competitor_answer",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_competitor_answer_question",
        "competitor_answer",
        [
            "attempt_id",
            "generated_test_question_id",
        ],
    )
