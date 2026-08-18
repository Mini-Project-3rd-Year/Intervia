"""
backend/app/models/resume_chunk.py
Phase 4 — SQLAlchemy ORM model for resume chunks stored with pgvector embeddings.

Table: resume_chunks
Vector dimension matches EMBEDDING_DIMENSION from config (default 768 for
Google text-embedding-004, or 1536 for OpenAI text-embedding-3-small/ada-002).
"""

from __future__ import annotations

import uuid
import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for all Intervia ORM models."""
    pass


class ResumeChunk(Base):
    """
    Stores one semantic chunk of a resume alongside its vector embedding.

    The `embedding` column is declared as a plain JSON array here so the
    model can be imported without the pgvector extension being installed
    (useful for unit tests with SQLite/mock DB).  In production the
    migration creates a proper vector(<dim>) column and index.
    """

    __tablename__ = "resume_chunks"

    id: str = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: str = Column(String, nullable=False, index=True)
    resume_id: str = Column(String, nullable=False, index=True)

    # The raw text that was embedded and will be inserted into the LLM prompt
    chunk_text: str = Column(Text, nullable=False)

    # Section label: experience | skills | project | education | summary
    chunk_type: str = Column(String(50), nullable=False)

    # Ordinal within the profile so we can reconstruct ordering
    chunk_index: int = Column(Integer, nullable=False, default=0)

    # Stored as a JSON array; the migration adds a proper vector column + index
    embedding: Optional[list] = Column(JSON, nullable=True)

    # Arbitrary section metadata (company, role, technologies, …)
    metadata_json: dict = Column(JSON, nullable=False, default=dict)

    created_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
