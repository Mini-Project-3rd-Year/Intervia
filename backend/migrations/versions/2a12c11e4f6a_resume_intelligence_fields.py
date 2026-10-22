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
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("resumes", "processed_at")
    op.drop_column("resumes", "status")
    op.drop_column("resumes", "parsed_profile")
    op.drop_column("resumes", "mime_type")
