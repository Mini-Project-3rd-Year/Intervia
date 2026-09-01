"""
backend/app/rag/rag_service.py
Phase 4 — RAG Orchestration Service

Ties together chunking, embedding, and persistence.
Called after a resume is uploaded and parsed.

Usage:
    chunks = await embed_and_store_resume(
        user_id=user_id,
        resume_id=resume_id,
        profile=candidate_profile,
        db=db,
    )
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.resume_chunk import ResumeChunk
from app.rag.chunker import chunk_resume
from app.rag.embedder import embed_batch
from app.schemas.candidate_profile import CandidateProfile

logger = get_logger()


async def embed_and_store_resume(
    user_id: str | uuid.UUID,
    resume_id: str | uuid.UUID,
    profile: CandidateProfile,
    db: AsyncSession,
) -> list[ResumeChunk]:
    """
    Full RAG ingestion pipeline for a single resume.

    Steps:
      1. Chunk the CandidateProfile into text segments
      2. Batch-embed all chunk texts in one (or a few) API call(s)
      3. Persist ResumeChunk rows to the database
      4. Delete any pre-existing chunks for this resume (idempotent re-upload)

    Args:
        user_id:   UUID of the authenticated user.
        resume_id: UUID of the resume record being processed.
        profile:   Structured candidate profile from the Resume Agent.
        db:        Async SQLAlchemy session.

    Returns:
        List of persisted ResumeChunk ORM instances.

    Raises:
        RuntimeError: If embedding API call fails.
        ValueError:   If no chunks can be derived from the profile.
    """
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    if isinstance(resume_id, str):
        resume_id = uuid.UUID(resume_id)

    logger.info(
        "RAG ingestion started",
        user_id=str(user_id),
        resume_id=str(resume_id),
    )

    # ── 1. Chunk the resume ───────────────────────────────────────────────────
    chunk_dicts = chunk_resume(profile)
    if not chunk_dicts:
        raise ValueError(
            f"No chunks could be derived from the resume profile for user {user_id}. "
            "Ensure the profile has at least one experience, skill, or project entry."
        )

    # ── 2. Delete stale chunks for this resume (idempotent) ──────────────────
    from sqlalchemy import delete

    await db.execute(
        delete(ResumeChunk).where(ResumeChunk.resume_id == resume_id)
    )
    logger.debug("Deleted stale chunks", resume_id=str(resume_id))

    # ── 3. Batch-embed all chunk texts ───────────────────────────────────────
    texts = [c["chunk_text"] for c in chunk_dicts]
    logger.info("Embedding %d chunks…", len(texts))
    embeddings = await embed_batch(texts)

    if len(embeddings) != len(chunk_dicts):
        raise RuntimeError(
            f"Embedding count mismatch: got {len(embeddings)} embeddings "
            f"for {len(chunk_dicts)} chunks."
        )

    # ── 4. Build and persist ORM objects ─────────────────────────────────────
    orm_chunks: list[ResumeChunk] = []
    for chunk_dict, embedding in zip(chunk_dicts, embeddings):
        chunk = ResumeChunk(
            user_id=user_id,
            resume_id=resume_id,
            chunk_text=chunk_dict["chunk_text"],
            chunk_type=chunk_dict["chunk_type"],
            embedding=embedding,
            metadata_json=chunk_dict["metadata_json"],
        )
        db.add(chunk)
        orm_chunks.append(chunk)

    await db.flush()  # assign PKs without committing (session.commit is caller's)

    logger.info(
        "RAG ingestion complete",
        user_id=str(user_id),
        resume_id=str(resume_id),
        chunk_count=len(orm_chunks),
    )

    return orm_chunks


async def delete_resume_chunks(
    resume_id: str | uuid.UUID,
    db: AsyncSession,
) -> int:
    """
    Remove all stored chunks for a given resume.
    Called when a resume is deleted.

    Returns the number of rows deleted.
    """
    from sqlalchemy import delete, func, select

    if isinstance(resume_id, str):
        resume_id = uuid.UUID(resume_id)

    result = await db.execute(
        delete(ResumeChunk)
        .where(ResumeChunk.resume_id == resume_id)
        .returning(ResumeChunk.id)
    )
    deleted = len(result.fetchall())
    logger.info("Deleted resume chunks", resume_id=str(resume_id), count=deleted)
    return deleted
