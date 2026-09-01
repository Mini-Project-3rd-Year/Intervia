"""
backend/app/api/v1/rag.py
Phase 4 — RAG Debug Endpoint

GET /api/v1/rag/test
  - Dev/debug only (requires DEBUG=true in settings)
  - Embeds the query string and returns the top-K matching resume chunks
  - Used to verify retrieval quality after resume upload

This router is NOT registered in production (DEBUG=false).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.rag.retriever import retrieve_resume_context

logger = get_logger()
settings = get_settings()

router = APIRouter(prefix="/rag", tags=["rag"])


# ── Response schemas ──────────────────────────────────────────────────────────

class ChunkResult(BaseModel):
    """A single retrieved resume chunk."""

    id: str
    chunk_type: str
    chunk_text: str
    metadata_json: dict

    model_config = {"from_attributes": True}


class RagTestResponse(BaseModel):
    """Response from the RAG test/debug endpoint."""

    query: str
    user_id: str
    top_k: int
    returned: int
    chunks: list[ChunkResult]


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get(
    "/test",
    response_model=RagTestResponse,
    summary="[DEV] Test RAG retrieval for a user and query",
    description=(
        "**Development only** (requires `DEBUG=true`). "
        "Embeds the query and returns the top-K most semantically similar "
        "resume chunks for the given user. "
        "Use this to verify embedding quality after uploading a resume."
    ),
    status_code=status.HTTP_200_OK,
)
async def test_rag_retrieval(
    user_id: str = Query(
        ...,
        description="UUID of the user whose resume chunks to search",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    query: str = Query(
        ...,
        description="Natural language retrieval query",
        examples=["Python and Kubernetes experience"],
        min_length=1,
        max_length=500,
    ),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of top results to return",
    ),
    resume_id: str | None = Query(
        default=None,
        description="Optional: restrict results to a specific resume UUID",
    ),
    db: AsyncSession = Depends(get_db),
) -> RagTestResponse:
    """
    Debug endpoint — retrieve the most relevant resume chunks for a query.

    Only available when DEBUG=true.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in DEBUG mode.",
        )

    try:
        chunks = await retrieve_resume_context(
            user_id=user_id,
            query=query,
            top_k=top_k,
            db=db,
            resume_id=resume_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.error("RAG retrieval failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding service error: {exc}",
        ) from exc

    chunk_results = [
        ChunkResult(
            id=str(chunk.id),
            chunk_type=chunk.chunk_type,
            chunk_text=chunk.chunk_text,
            metadata_json=chunk.metadata_json or {},
        )
        for chunk in chunks
    ]

    return RagTestResponse(
        query=query,
        user_id=user_id,
        top_k=top_k,
        returned=len(chunk_results),
        chunks=chunk_results,
    )
