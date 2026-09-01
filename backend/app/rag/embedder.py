"""
backend/app/rag/embedder.py
Phase 4 — Text Embedding

Provides embed_text() and embed_batch() for converting text into
high-dimensional float vectors suitable for cosine similarity search.

Provider selection:
  - LLM_PROVIDER=gemini  → Google text-embedding-004   (768-dim)
  - LLM_PROVIDER=openai  → OpenAI text-embedding-ada-002 (1536-dim)

Ensure EMBEDDING_DIMENSION in settings matches the chosen model:
  - models/text-embedding-004  → 768
  - text-embedding-ada-002     → 1536
"""

from __future__ import annotations

import asyncio
import functools

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()
settings = get_settings()

# Batch size for embedding API calls
_BATCH_SIZE = 50


# ── Google Gemini embedder (google-genai SDK) ─────────────────────────────────

def _get_google_client():
    """Lazily initialise google-genai client."""
    try:
        from google import genai  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Run: pip install google-genai"
        ) from exc

    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file to use Google embeddings."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _embed_google_sync(texts: list[str]) -> list[list[float]]:
    """Synchronous Google embedding call (runs in thread pool)."""
    client = _get_google_client()
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=texts,
    )
    # result.embeddings is a list of ContentEmbedding objects
    embeddings = result.embeddings
    if not embeddings:
        raise RuntimeError("Google embedding API returned an empty response.")
    return [list(e.values) for e in embeddings]


# ── OpenAI embedder ───────────────────────────────────────────────────────────

def _get_openai_client():
    try:
        from openai import OpenAI  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "openai is not installed. Run: pip install openai"
        ) from exc

    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file to use OpenAI embeddings."
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _embed_openai_sync(texts: list[str]) -> list[list[float]]:
    """Synchronous OpenAI embedding call (runs in thread pool)."""
    client = _get_openai_client()
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# ── Async public API ──────────────────────────────────────────────────────────

async def embed_text(text: str) -> list[float]:
    """
    Embed a single piece of text into a float vector.

    Runs the blocking API call in a thread pool so it doesn't block
    the FastAPI event loop.

    Args:
        text: The text string to embed.

    Returns:
        A list of floats of length EMBEDDING_DIMENSION.
    """
    embeddings = await embed_batch([text])
    return embeddings[0]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts in batches for efficiency.

    Args:
        texts: A list of text strings to embed.

    Returns:
        A list of embedding vectors in the same order as the input.

    Raises:
        ValueError: If texts is empty.
        RuntimeError: If the API key is missing or any batch call fails.
    """
    if not texts:
        raise ValueError("embed_batch() called with an empty list.")

    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        sync_fn = _embed_google_sync
    elif provider == "openai":
        sync_fn = _embed_openai_sync
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER={provider!r}. "
            "Supported values: 'gemini', 'openai'."
        )

    loop = asyncio.get_event_loop()
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        logger.debug(
            "Embedding batch",
            provider=provider,
            batch_index=i // _BATCH_SIZE,
            batch_size=len(batch),
        )
        batch_embeddings = await loop.run_in_executor(
            None,
            functools.partial(sync_fn, batch),
        )
        all_embeddings.extend(batch_embeddings)

    return all_embeddings



def _embed_openai_sync(texts: list[str]) -> list[list[float]]:
    """Synchronous OpenAI embedding call (runs in thread pool)."""
    client = _get_openai_client()
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,  # e.g. "text-embedding-ada-002"
        input=texts,
    )
    return [item.embedding for item in response.data]


# ── Async public API ──────────────────────────────────────────────────────────

async def embed_text(text: str) -> list[float]:
    """
    Embed a single piece of text into a float vector.

    Runs the blocking API call in a thread pool so it doesn't block
    the FastAPI event loop.

    Args:
        text: The text string to embed.

    Returns:
        A list of floats of length EMBEDDING_DIMENSION.

    Raises:
        RuntimeError: If the embedding API key is missing or the call fails.
    """
    embeddings = await embed_batch([text])
    return embeddings[0]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts in batches for efficiency.

    Args:
        texts: A list of text strings to embed.

    Returns:
        A list of embedding vectors in the same order as the input.

    Raises:
        RuntimeError: If the API key is missing or any batch call fails.
        ValueError: If texts is empty.
    """
    if not texts:
        raise ValueError("embed_batch() called with an empty list.")

    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        sync_fn = _embed_google_sync
    elif provider == "openai":
        sync_fn = _embed_openai_sync
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER={provider!r}. "
            "Supported values: 'gemini', 'openai'."
        )

    # Split into batches and call the sync function in the thread pool
    loop = asyncio.get_event_loop()
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        logger.debug(
            "Embedding batch",
            provider=provider,
            batch_index=i // _BATCH_SIZE,
            batch_size=len(batch),
        )
        batch_embeddings = await loop.run_in_executor(
            None,
            functools.partial(sync_fn, batch),
        )
        all_embeddings.extend(batch_embeddings)

    return all_embeddings
