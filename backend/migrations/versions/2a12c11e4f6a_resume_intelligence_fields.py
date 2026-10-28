"""Add resume processing and profile fields."""

from alembic import op
import sqlalchemy as sa


revision = "2a12c11e4f6a"
down_revision = "1f7ec57c373b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("mime_type", sa.String(length=100), nullable=True))
    op.add_column("resumes", sa.Column("parsed_profile", sa.JSON(), nullable=True))
    op.add_column(
        "resumes",
        sa.Column(
            "status",
            sa.String(length=50),
            server_default="ready",
            nullable=False,
        ),
    )
    op.add_column(
        "resumes",
        sa.Column("ai_processing_consent", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "resumes",
        sa.Column("processed_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "resume_daily_usage",
        sa.Column("user_id", sa.String(length=36), primary_key=True),
        sa.Column("usage_date", sa.Date(), primary_key=True),
        sa.Column("uploads", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("profile_extractions", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("resumes", "processed_at")
    op.drop_column("resumes", "ai_processing_consent")
    op.drop_column("resumes", "status")
    op.drop_column("resumes", "parsed_profile")
    op.drop_column("resumes", "mime_type")
    op.drop_table("resume_daily_usage")
