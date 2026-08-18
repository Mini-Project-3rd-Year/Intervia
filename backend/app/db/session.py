"""
backend/app/db/session.py
Phase 4 — Async SQLAlchemy engine and session factory.

Uses DATABASE_URL from config. Import `get_db_session` as a FastAPI dependency
for routes that need database access.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Engine — created lazily; reused for the lifetime of the process.
# ---------------------------------------------------------------------------

_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

_AsyncSessionLocal = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context-manager that yields a database session and handles commit/rollback.

    Usage in FastAPI routes (via Depends):

        async def my_route(session: AsyncSession = Depends(get_db_session_dep)):
            ...

    Usage in services / agents:

        async with get_db_session() as session:
            ...
    """
    async with _AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db_session_dep() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency wrapper around get_db_session."""
    async with get_db_session() as session:
        yield session
