"""
backend/app/rag/retriever.py
Phase 4 — Vector Retrieval

Retrieves the most semantically relevant resume chunks for a given query
using cosine similarity via pgvector's <=> operator.

Usage:
    chunks = await retrieve_resume_context(
        user_id=user_id,
        query="Python and Kubernetes experience",
        top_k=5,
        db=db,
    )
"""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.resume_chunk import ResumeChunk
from app.rag.embedder import embed_text

logger = get_logger()
settings = get_settings()


async def retrieve_resume_context(
    user_id: str | uuid.UUID,
    query: str,
    top_k: int = 5,
    db: AsyncSession = None,  # type: ignore[assignment]
    resume_id: str | uuid.UUID | None = None,
) -> list[ResumeChunk]:
    """
    Find the top-K resume chunks most semantically similar to `query`.

    Uses pgvector's cosine distance operator (<=>) to rank chunks.
    A lower cosine distance score = more similar.

    Args:
        user_id:   UUID of the authenticated user (scopes results to their data).
        query:     Natural language query string, e.g. "Python experience".
        top_k:     Maximum number of chunks to return (default 5).
        db:        Async SQLAlchemy session (injected via FastAPI Depends).
        resume_id: Optional — restrict results to a specific resume upload.

    Returns:
        List of ResumeChunk ORM instances, ordered by similarity (most → least).

    Raises:
        ValueError: If top_k < 1 or query is empty.
        RuntimeError: If the embedding API call fails.
    """
    if not query or not query.strip():
        raise ValueError("retrieve_resume_context: query must not be empty.")
    if top_k < 1:
        raise ValueError(f"retrieve_resume_context: top_k must be >= 1, got {top_k}.")

    # Convert user_id to UUID if passed as string
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)

    logger.info(
        "RAG retrieval",
        user_id=str(user_id),
        query_preview=query[:80],
        top_k=top_k,
    )

    # ── 1. Embed the query ────────────────────────────────────────────────────
    query_embedding = await embed_text(query)

    # ── 2. Build cosine similarity query ─────────────────────────────────────
    # pgvector's <=> is the cosine DISTANCE (0=identical, 2=opposite).
    # We order ASC to get closest chunks first.
    query_vector = cast(query_embedding, Vector(settings.EMBEDDING_DIMENSION))

    stmt = (
        select(ResumeChunk)
        .where(ResumeChunk.user_id == user_id)
        .where(ResumeChunk.embedding.is_not(None))
    )

    if resume_id is not None:
        if isinstance(resume_id, str):
            resume_id = uuid.UUID(resume_id)
        stmt = stmt.where(ResumeChunk.resume_id == resume_id)

    stmt = (
        stmt
        .order_by(ResumeChunk.embedding.op("<=>")(query_vector))
        .limit(top_k)
    )

    result = await db.execute(stmt)
    chunks: list[ResumeChunk] = list(result.scalars().all())

    logger.info(
        "RAG retrieval complete",
        returned=len(chunks),
        requested=top_k,
    )

    return chunks
