"""
backend/app/models/resume_chunk.py
Phase 4 — RAG System

SQLAlchemy ORM model for the resume_chunks table.
Stores resume text chunks and their pgvector embeddings for semantic retrieval.
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.session import Base

_settings = get_settings()


class ResumeChunk(Base):
    """
    Represents a single semantic chunk of a resume, together with its
    pgvector embedding.

    Chunking strategy (see rag/chunker.py):
      - One chunk per WorkExperience entry
      - One chunk per skill group
      - One chunk per Project
      - Optional: one chunk for the education / summary section

    The embedding column uses pgvector's Vector type so that cosine similarity
    queries can be executed directly in SQL via the <=> operator.
    """

    __tablename__ = "resume_chunks"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign keys (loose — Phase 5 will add proper FK constraints) ─────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Owning user — matches users.id (FK enforced in Phase 5)",
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Source resume — matches resumes.id (FK enforced in Phase 5)",
    )

    # ── Content ───────────────────────────────────────────────────────────────
    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Raw text of this resume chunk",
    )
    chunk_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="experience | skills | projects | education | summary",
    )

    # ── Embedding ─────────────────────────────────────────────────────────────
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(_settings.EMBEDDING_DIMENSION),
        nullable=True,
        comment=f"pgvector {_settings.EMBEDDING_DIMENSION}-dim embedding",
    )

    # ── Metadata ──────────────────────────────────────────────────────────────
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Arbitrary metadata (company name, date range, skill names, …)",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<ResumeChunk id={self.id!s:.8} "
            f"type={self.chunk_type!r} "
            f"user={self.user_id!s:.8}>"
        )
