"""add interview engine columns

Revision ID: a0fdd6388fe1
Revises: 1f7ec57c373b
Create Date: 2026-10-13 07:11:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a0fdd6388fe1"
down_revision: Union[str, None] = "1f7ec57c373b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Candidate role targeted for the interview
    op.add_column("interviews", sa.Column("role", sa.String(length=255), nullable=True))

    # 2. Text-to-speech audio URL for the asked question
    op.add_column("interview_questions", sa.Column("audio_url", sa.String(length=500), nullable=True))

    # 3-6. Answer-level score, feedback, and structured strengths/improvements
    op.add_column("interview_answers", sa.Column("score", sa.Integer(), nullable=True))
    op.add_column("interview_answers", sa.Column("feedback", sa.Text(), nullable=True))
    op.add_column(
        "interview_answers",
        sa.Column("strengths", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.add_column(
        "interview_answers",
        sa.Column("improvements", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade() -> None:
    op.drop_column("interview_answers", "improvements")
    op.drop_column("interview_answers", "strengths")
    op.drop_column("interview_answers", "feedback")
    op.drop_column("interview_answers", "score")
    op.drop_column("interview_questions", "audio_url")
    op.drop_column("interviews", "role")
