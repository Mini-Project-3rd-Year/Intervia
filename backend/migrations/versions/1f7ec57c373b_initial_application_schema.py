"""initial application schema

Revision ID: 1f7ec57c373b
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "1f7ec57c373b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("supabase_user_id", sa.String(36), nullable=False, unique=True),
        sa.Column("full_name", sa.String(100)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "resumes",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("raw_text", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("resume_id", sa.UUID(), sa.ForeignKey("resumes.id"), unique=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("projects", sa.JSON(), nullable=False),
        sa.Column("experience", sa.JSON(), nullable=False),
        sa.Column("education", sa.JSON(), nullable=False),
        sa.Column("certifications", sa.JSON(), nullable=False),
        sa.Column("achievements", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("role", sa.String(255)),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("preferred_skills", sa.JSON(), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("skill_gaps", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "interviews",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("resume_id", sa.UUID()),
        sa.Column("job_id", sa.UUID()),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer()),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("strategy", sa.JSON()),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("overall_score", sa.Numeric(5, 2)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "interview_questions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("interview_id", sa.UUID(), sa.ForeignKey("interviews.id"), nullable=False, index=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("difficulty", sa.Integer()),
        sa.Column("source", sa.String(100)),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("asked_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "interview_answers",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("question_id", sa.UUID(), sa.ForeignKey("interview_questions.id"), nullable=False, index=True),
        sa.Column("transcript", sa.Text()),
        sa.Column("audio_url", sa.Text()),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "interview_evaluations",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("answer_id", sa.UUID(), sa.ForeignKey("interview_answers.id"), nullable=False, unique=True),
        sa.Column("relevance", sa.Numeric(5, 2), nullable=False),
        sa.Column("technical_accuracy", sa.Numeric(5, 2), nullable=False),
        sa.Column("clarity", sa.Numeric(5, 2), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("interview_evaluations")
    op.drop_table("interview_answers")
    op.drop_table("interview_questions")
    op.drop_table("interviews")
    op.drop_table("job_descriptions")
    op.drop_table("candidate_profiles")
    op.drop_table("resumes")
    op.drop_table("user_profiles")
