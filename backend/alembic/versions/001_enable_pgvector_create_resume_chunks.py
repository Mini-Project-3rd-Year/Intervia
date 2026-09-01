"""
001_enable_pgvector_create_resume_chunks

Phase 4 — RAG System
- Enables the pgvector extension
- Creates the resume_chunks table with a 768-dim vector column
- Adds an IVFFlat index for fast approximate cosine nearest-neighbor search

Revision ID: 001
Revises: (initial)
Create Date: 2026-09-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Embedding dimension from project config (text-embedding-004 → 768)
EMBEDDING_DIM = 768


def upgrade() -> None:
    # ── 1. Enable pgvector extension ─────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # ── 2. Create resume_chunks table ─────────────────────────────────────────
    op.create_table(
        "resume_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column(
            "chunk_type",
            sa.String(50),
            nullable=False,
            comment="experience | skills | projects | education | summary",
        ),
        sa.Column(
            "embedding",
            Vector(EMBEDDING_DIM),
            nullable=True,
            comment=f"pgvector {EMBEDDING_DIM}-dim embedding (text-embedding-004)",
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # ── 3. IVFFlat index for approximate cosine similarity ────────────────────
    # lists=100 is a reasonable default; tune based on dataset size.
    op.execute(
        """
        CREATE INDEX resume_chunks_embedding_idx
        ON resume_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS resume_chunks_embedding_idx;")
    op.drop_table("resume_chunks")
    # Note: we intentionally do NOT drop the vector extension on downgrade
    # as other tables may depend on it.
