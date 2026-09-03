"""add English topic names

Revision ID: 7c9f4a1d2e6b
Revises: 4143cd27578e
Create Date: 2026-09-03 14:22:57

"""

from alembic import op
import sqlalchemy as sa


revision = "7c9f4a1d2e6b"
down_revision = "4143cd27578e"
branch_labels = None
depends_on = None


TOPIC_TRANSLATIONS = {
    "Matematika": "Mathematics",
    "Természetismeret": "Natural Science",
    "Magyar nyelv": "Hungarian Language",
    "Történelem": "History",
    "Logika": "Logic",
    "Általános műveltség": "General Knowledge",
    "Informatika": "Computer Science",
    "Sport": "Sports",
}


def upgrade():
    op.add_column(
        "topic",
        sa.Column(
            "name_en",
            sa.String(length=100),
            nullable=True,
        ),
    )

    topic = sa.table(
        "topic",
        sa.column("name", sa.String(length=100)),
        sa.column("name_en", sa.String(length=100)),
    )

    for name_hu, name_en in TOPIC_TRANSLATIONS.items():
        op.execute(
            topic.update()
            .where(topic.c.name == name_hu)
            .values(name_en=name_en)
        )


def downgrade():
    op.drop_column(
        "topic",
        "name_en",
    )
